import { useEffect, useState } from 'react'
import { usePlatform } from '../../context/PlatformContext'
import { platformAPI } from '../../lib/api'
import PaginatedTable from '../../components/PaginatedTable'

export default function PlatformSecondarySales() {
  const config = usePlatform()
  const [stats, setStats] = useState({ sells: 0 })
  const [loading, setLoading] = useState(true)

  const tableName = config.tables?.secondarySells

  useEffect(() => {
    setLoading(true)
    platformAPI.getStats(config.slug)
      .then((data) => setStats(data))
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [config])

  return (
    <>
      <div className="plat-page-header">
        <h1>Secondary Sells</h1>
        <p>
          {config.name} secondary sales &middot;{' '}
          {loading ? 'loading...' : `${(stats.sells || 0).toLocaleString()} records`}
        </p>
      </div>
      <div className="plat-content">
        {tableName ? (
          <PaginatedTable key={tableName} tableName={tableName} />
        ) : (
          <div className="card">
            <div className="table-status">No secondary sales table configured for {config.name}</div>
          </div>
        )}
      </div>
    </>
  )
}
