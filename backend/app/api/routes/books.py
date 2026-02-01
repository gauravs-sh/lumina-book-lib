from __future__ import annotations

from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, HTTPException, Request, UploadFile, status
from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db, get_llm, get_storage
from app.models.borrow import BookBorrow
from app.models.book import Book
from app.models.review import Review
from app.schemas.book import BookListResponse, BookRead, BookSummaryRead, BookUpdate
from app.schemas.borrow import BorrowRead, BorrowStatusRead
from app.schemas.review import ReviewRead
from app.db.session import SessionLocal
from app.services.summarizer import generate_summary
from app.services.text_extraction import extract_text

router = APIRouter(prefix="/books", tags=["books"])


async def _update_book_summary(book_id: int, content: str) -> None:
    llm = await get_llm()
    summary = await generate_summary(content, llm)
    async with SessionLocal() as session:
        result = await session.execute(select(Book).where(Book.id == book_id))
        book = result.scalar_one_or_none()
        if book:
            book.summary = summary
            await session.commit()


@router.post("", response_model=BookRead, status_code=status.HTTP_201_CREATED)
async def create_book(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    title: str = Form(...),
    author: str = Form(...),
    genre: str = Form(...),
    year_published: int = Form(...),
    session: AsyncSession = Depends(get_db),
    _: str = Depends(get_current_user),
    storage=Depends(get_storage),
) -> Book:
    content_bytes = await file.read()
    extracted_text, content_type = extract_text(file.filename, content_bytes)
    storage_key = await storage.save(file.filename, content_bytes)

    book = Book(
        title=title,
        author=author,
        genre=genre,
        year_published=year_published,
        file_key=storage_key,
        file_name=file.filename,
        content_type=content_type,
        file_size=len(content_bytes),
        content_text=extracted_text,
    )
    session.add(book)
    await session.commit()
    await session.refresh(book)

    if extracted_text:
        background_tasks.add_task(_update_book_summary, book.id, extracted_text)

    return book


@router.get("", response_model=BookListResponse)
async def list_books(
    page: int = 1,
    size: int = 10,
    session: AsyncSession = Depends(get_db),
) -> BookListResponse:
    page = max(page, 1)
    size = min(max(size, 1), 50)
    total_result = await session.execute(select(func.count(Book.id)))
    total = total_result.scalar_one()
    result = await session.execute(select(Book).offset((page - 1) * size).limit(size))
    items = list(result.scalars().all())
    return BookListResponse(items=items, page=page, size=size, total=total)


@router.get("/{book_id}", response_model=BookRead)
async def get_book(book_id: int, session: AsyncSession = Depends(get_db)) -> Book:
    result = await session.execute(select(Book).where(Book.id == book_id))
    book = result.scalar_one_or_none()
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    return book


@router.put("/{book_id}", response_model=BookRead)
async def update_book(
    book_id: int,
    request: Request,
    background_tasks: BackgroundTasks,
    file: UploadFile | None = File(default=None),
    title: str | None = Form(default=None),
    author: str | None = Form(default=None),
    genre: str | None = Form(default=None),
    year_published: int | None = Form(default=None),
    session: AsyncSession = Depends(get_db),
    _: str = Depends(get_current_user),
    storage=Depends(get_storage),
) -> Book:
    result = await session.execute(select(Book).where(Book.id == book_id))
    book = result.scalar_one_or_none()
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")

    if request.headers.get("content-type", "").startswith("application/json"):
        payload = BookUpdate.model_validate(await request.json())
        updates = payload.model_dump(exclude_unset=True)
    else:
        updates = {
            "title": title,
            "author": author,
            "genre": genre,
            "year_published": year_published,
        }
        updates = {key: value for key, value in updates.items() if value is not None}

    for field, value in updates.items():
        setattr(book, field, value)

    if file is not None:
        content_bytes = await file.read()
        extracted_text, content_type = extract_text(file.filename, content_bytes)
        storage_key = await storage.save(file.filename, content_bytes)
        if book.file_key:
            await storage.delete(book.file_key)
        book.file_key = storage_key
        book.file_name = file.filename
        book.content_type = content_type
        book.file_size = len(content_bytes)
        book.content_text = extracted_text
        if extracted_text:
            background_tasks.add_task(_update_book_summary, book.id, extracted_text)

    await session.commit()
    await session.refresh(book)
    return book


@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(
    book_id: int,
    session: AsyncSession = Depends(get_db),
    _: str = Depends(get_current_user),
    storage=Depends(get_storage),
) -> None:
    result = await session.execute(select(Book).where(Book.id == book_id))
    book = result.scalar_one_or_none()
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    if book.file_key:
        await storage.delete(book.file_key)
    await session.execute(delete(Review).where(Review.book_id == book_id))
    await session.execute(delete(BookBorrow).where(BookBorrow.book_id == book_id))
    await session.delete(book)
    await session.commit()


@router.get("/{book_id}/reviews", response_model=list[ReviewRead])
async def list_reviews(book_id: int, session: AsyncSession = Depends(get_db)) -> list[Review]:
    result = await session.execute(select(Review).where(Review.book_id == book_id))
    return list(result.scalars().all())


@router.get("/{book_id}/summary", response_model=BookSummaryRead)
async def get_book_summary(book_id: int, session: AsyncSession = Depends(get_db)) -> BookSummaryRead:
    result = await session.execute(select(Book).where(Book.id == book_id))
    book = result.scalar_one_or_none()
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")

    review_result = await session.execute(select(Review).where(Review.book_id == book_id))
    reviews = list(review_result.scalars().all())
    average_rating = sum(review.rating for review in reviews) / len(reviews) if reviews else 0.0

    return BookSummaryRead(
        book_id=book.id,
        summary=book.summary,
        review_summary=book.review_summary,
        average_rating=round(average_rating, 2),
        total_reviews=len(reviews),
    )


@router.get("/{book_id}/analysis", response_model=BookSummaryRead)
async def get_book_analysis(book_id: int, session: AsyncSession = Depends(get_db)) -> BookSummaryRead:
    return await get_book_summary(book_id, session)


@router.post("/{book_id}/borrow", response_model=BorrowRead)
async def borrow_book(
    book_id: int,
    session: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
) -> BookBorrow:
    result = await session.execute(select(Book).where(Book.id == book_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")

    active_borrow = await session.execute(
        select(BookBorrow).where(
            BookBorrow.book_id == book_id,
            BookBorrow.user_id == user.id,
            BookBorrow.returned_at.is_(None),
        )
    )
    if active_borrow.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Book already borrowed")

    borrow = BookBorrow(book_id=book_id, user_id=user.id)
    session.add(borrow)
    await session.commit()
    await session.refresh(borrow)
    return borrow


@router.post("/{book_id}/return", response_model=BorrowRead)
async def return_book(
    book_id: int,
    session: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
) -> BookBorrow:
    result = await session.execute(
        select(BookBorrow).where(
            BookBorrow.book_id == book_id,
            BookBorrow.user_id == user.id,
            BookBorrow.returned_at.is_(None),
        )
    )
    borrow = result.scalar_one_or_none()
    if not borrow:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No active borrow found")
    borrow.returned_at = func.now()
    await session.commit()
    await session.refresh(borrow)
    return borrow


@router.get("/{book_id}/borrow-status", response_model=BorrowStatusRead)
async def get_borrow_status(
    book_id: int,
    session: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
) -> BorrowStatusRead:
    result = await session.execute(
        select(BookBorrow)
        .where(
            BookBorrow.book_id == book_id,
            BookBorrow.user_id == user.id,
        )
        .order_by(BookBorrow.borrowed_at.desc())
    )
    borrow = result.scalars().first()
    if not borrow:
        return BorrowStatusRead(status="Available")
    if borrow.returned_at is None:
        return BorrowStatusRead(status="Borrowed", borrowed_at=borrow.borrowed_at)
    return BorrowStatusRead(status="Returned", borrowed_at=borrow.borrowed_at, returned_at=borrow.returned_at)


@router.delete("/{book_id}/file", response_model=BookRead)
async def delete_book_file(
    book_id: int,
    session: AsyncSession = Depends(get_db),
    _: str = Depends(get_current_user),
    storage=Depends(get_storage),
) -> Book:
    result = await session.execute(select(Book).where(Book.id == book_id))
    book = result.scalar_one_or_none()
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    if book.file_key:
        await storage.delete(book.file_key)
    book.file_key = None
    book.file_name = None
    book.content_type = None
    book.file_size = None
    book.content_text = None
    await session.commit()
    await session.refresh(book)
    return book
