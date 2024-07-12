import { getCsrfToken } from "./api";

const CSRFToken = () => {
  const csrf_token = getCsrfToken();
  return (
    <input type="hidden" name="csrfmiddlewaretoken" value={csrf_token} />
  )
}

export default CSRFToken