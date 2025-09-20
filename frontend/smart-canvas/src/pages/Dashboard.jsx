import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { getProfile } from "../utils/api";

export default function Dashboard() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    async function fetchProfile() {
      const token = localStorage.getItem("token");
      if (!token) {
        navigate("/login");
        return;
      }

      const res = await getProfile();
      if (res && res.email) {
        setUser(res);
      } else {
        localStorage.removeItem("token"); // invalid/expired token
        navigate("/login");
      }
      setLoading(false);
    }

    fetchProfile();
  }, [navigate]);

  if (loading) return <p>Loading...</p>;

  return (
    <div className="dashboard">
      <h2>Dashboard</h2>
      {user ? (
        <>
          <p>Welcome, {user.name || "User"}!</p>
          <p>Email: {user.email}</p>
        </>
      ) : (
        <p>Redirecting...</p>
      )}
    </div>
  );
}
