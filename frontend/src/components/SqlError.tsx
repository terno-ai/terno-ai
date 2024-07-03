const SqlError = ({ error }: { error: string }) => {
  if (error == "") {
    return null;
  }
  else {
    return (
      <div>
        <div>Error: {error}</div>
      </div>
    );
  }
};

export default SqlError;
