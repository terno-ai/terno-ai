import { useEffect, useState } from "react";
import { getUserDetails } from "../utils/api";

const useUserDetails = () => {
  const [user, setUser] = useState({id: '', username: ''});

  useEffect(() => {
    const fetchUserDetails = async () => {
      const response = await getUserDetails();
      setUser(response);
    };
    fetchUserDetails();
  }, []);

  return [user];
}

export default useUserDetails