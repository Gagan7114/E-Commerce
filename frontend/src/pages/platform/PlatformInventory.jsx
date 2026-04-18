import { useEffect, useState } from 'react'
import { usePlatform } from '../../context/PlatformContext'
import { platformAPI } from '../../lib/api'
import PaginatedTable from '../../components/PaginatedTable'

export default function PlatformInventory() {
  const config = usePlatform()
  const [stats, setStats] = useState({ inventory: 0 })
  const [loading, setLoading] = useState(true)

  const tableName = config.tables?.inventory

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
        <h1>Inventory</h1>
        <p>
          {config.name} inventory &middot;{' '}
          {loading ? 'loading...' : `${(stats.inventory || 0).toLocaleString()} items`}
        </p>
      </div>
      <div className="plat-content">
        {tableName ? (
          <PaginatedTable key={tableName} tableName={tableName} />
        ) : (
          <div className="card">
            <div className="table-status">No inventory table configured for {config.name}</div>
          </div>
        )}
      </div>
    </>
  )
}
