const SqlError = ({error}: {error: string}) => {
  return (
    <div>
        <div>{error}</div>
    </div>
  )
}

export default SqlError