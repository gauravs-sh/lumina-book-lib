import { Route, Routes } from "react-router-dom";
import { AuthProvider } from "./components/AuthProvider";
import Layout from "./components/Layout";
import Books from "./pages/Books";
import Documents from "./pages/Documents";
import Home from "./pages/Home";
import Ingestion from "./pages/Ingestion";
import Login from "./pages/Login";
import Qa from "./pages/Qa";
import Signup from "./pages/Signup";
import Users from "./pages/Users";

export default function App() {
  return (
    <AuthProvider>
      <Layout>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/login" element={<Login />} />
          <Route path="/signup" element={<Signup />} />
          <Route path="/books" element={<Books />} />
          <Route path="/documents" element={<Documents />} />
          <Route path="/ingestion" element={<Ingestion />} />
          <Route path="/qa" element={<Qa />} />
          <Route path="/users" element={<Users />} />
        </Routes>
      </Layout>
    </AuthProvider>
  );
}
