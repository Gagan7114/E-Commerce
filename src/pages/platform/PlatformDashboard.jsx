import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { usePlatform } from '../../context/PlatformContext'
import { supabase } from '../../lib/supabase'

export default function PlatformDashboard() {
  const config = usePlatform()
  const [stats, setStats] = useState({ inventory: 0, sells: 0, openPOs: 0, activeTrucks: 0 })
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function load() {
      setLoading(true)
      const [inv, sells, pos, trucks] = await Promise.all([
        supabase.from(config.tables.inventory).select('*', { count: 'exact', head: true }),
        supabase.from(config.tables.secondarySells).select('*', { count: 'exact', head: true }),
        supabase.from(config.tables.masterPO).select('*', { count: 'exact', head: true })
          .ilike(config.poFilterColumn, `%${config.poFilterValue}%`),
        supabase.from(config.tables.dispatches).select('*', { count: 'exact', head: true })
          .eq('platform', config.slug).eq('status', 'loading'),
      ])
      setStats({
        inventory: inv.count || 0,
        sells: sells.count || 0,
        openPOs: pos.count || 0,
        activeTrucks: trucks.count || 0,
      })
      setLoading(false)
    }
    load()
  }, [config])

  return (
    <>
      <div className="plat-page-header">
        <h1>{config.name} Dashboard</h1>
        <p>Overview of {config.name} platform operations</p>
      </div>
      <div className="plat-content">
        {/* Summary cards */}
        <div className="plat-cards">
          <Link to={`/platform/${config.slug}/po`} className="plat-card">
            <span className="plat-card-value">{loading ? '...' : stats.openPOs.toLocaleString()}</span>
            <span className="plat-card-label">Purchase Orders</span>
          </Link>
          <div className="plat-card">
            <span className="plat-card-value">{loading ? '...' : stats.inventory.toLocaleString()}</span>
            <span className="plat-card-label">Inventory Items</span>
          </div>
          <div className="plat-card">
            <span className="plat-card-value">{loading ? '...' : stats.sells.toLocaleString()}</span>
            <span className="plat-card-label">Secondary Sells</span>
          </div>
          <Link to={`/platform/${config.slug}/truck-loading`} className="plat-card">
            <span className="plat-card-value">{loading ? '...' : stats.activeTrucks}</span>
            <span className="plat-card-label">Active Truck Loadings</span>
          </Link>
        </div>

        {/* Quick links */}
        <div className="plat-quick-links">
          <Link to={`/platform/${config.slug}/po`} className="plat-quick-link">
            <span className="plat-quick-link-icon">&#128230;</span>
            PO &amp; Stock Management
          </Link>
          <Link to={`/platform/${config.slug}/truck-loading`} className="plat-quick-link">
            <span className="plat-quick-link-icon">&#128666;</span>
            Truck Loading
          </Link>
          <Link to={`/platform/${config.slug}/dispatches`} className="plat-quick-link">
            <span className="plat-quick-link-icon">&#128203;</span>
            Dispatch History
          </Link>
        </div>
      </div>
    </>
  )
}
