import { Navigate, Route, Routes } from "react-router";
import NavBar from "./components/NavBar";
import { useAuth } from "./auth";
import Catalog from "./pages/Catalog";
import EventDetail from "./pages/EventDetail";
import Login from "./pages/Login";
import MyTickets from "./pages/MyTickets";
import Checkout from "./pages/Checkout";
import Confirmation from "./pages/Confirmation";
import AdminDashboard from "./pages/admin/AdminDashboard";
import AdminEventForm from "./pages/admin/AdminEventForm";
import AdminEventManage from "./pages/admin/AdminEventManage";
import AdminPromos from "./pages/admin/AdminPromos";

function Protected({ children }) {
  const { user, ready } = useAuth();
  if (!ready) return null;
  return user ? children : <Navigate to="/login" replace />;
}

function Staff({ children }) {
  const { user, ready } = useAuth();
  if (!ready) return null;
  if (!user) return <Navigate to="/login" replace />;
  if (!["organizer", "admin"].includes(user.role)) return <Navigate to="/" replace />;
  return children;
}

export default function App() {
  return (
    <>
      <NavBar />
      <Routes>
        <Route path="/" element={<Catalog />} />
        <Route path="/events/:id" element={<EventDetail />} />
        <Route path="/login" element={<Login />} />
        <Route path="/checkout/:orderId" element={<Protected><Checkout /></Protected>} />
        <Route path="/confirmation/:orderId" element={<Protected><Confirmation /></Protected>} />
        <Route path="/admin" element={<Staff><AdminDashboard /></Staff>} />
        <Route path="/admin/events/new" element={<Staff><AdminEventForm /></Staff>} />
        <Route path="/admin/events/:id" element={<Staff><AdminEventManage /></Staff>} />
        <Route path="/admin/events/:id/edit" element={<Staff><AdminEventForm /></Staff>} />
        <Route path="/admin/promos" element={<Staff><AdminPromos /></Staff>} />
        <Route path="/tickets" element={<Protected><MyTickets /></Protected>} />
      </Routes>
    </>
  );
}
