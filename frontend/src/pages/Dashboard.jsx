function Dashboard() {
  return (
    <div className="min-h-screen bg-gray-100 p-8">

      <h1 className="text-3xl font-bold text-gray-800">
        Attendance Dashboard
      </h1>

      <p className="text-gray-500 mt-2">
        Welcome to the Attendance Management System
      </p>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mt-8">

        <div className="bg-white p-6 rounded-xl shadow">
          <p className="text-gray-500">Total Students</p>
          <h2 className="text-3xl font-bold mt-2">120</h2>
        </div>

        <div className="bg-white p-6 rounded-xl shadow">
          <p className="text-gray-500">Present Today</p>
          <h2 className="text-3xl font-bold mt-2">105</h2>
        </div>

        <div className="bg-white p-6 rounded-xl shadow">
          <p className="text-gray-500">Absent Today</p>
          <h2 className="text-3xl font-bold mt-2">15</h2>
        </div>

        <div className="bg-white p-6 rounded-xl shadow">
          <p className="text-gray-500">Attendance Rate</p>
          <h2 className="text-3xl font-bold mt-2">87.5%</h2>
        </div>

      </div>

    </div>
  )
}

export default Dashboard