import { Navigate, useLocation } from "react-router-dom";

const ProviderCallback = () => {
  const location = useLocation();
  const params = new URLSearchParams(location.search);
  const error = params.get("error");

  let url = "/accounts/login/";
  if (!error) {
    return <Navigate to={'/'} />;
  }
  return (
    <>
      <h1>Third-Party Login Failure</h1>
      <p>Something went wrong. {error}</p>
      <a href={url}>Continue</a>
    </>
  );
};

export default ProviderCallback;
