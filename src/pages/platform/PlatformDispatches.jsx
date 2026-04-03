import { useEffect, useState, useCallback } from 'react'
import { usePlatform } from '../../context/PlatformContext'
import { supabase } from '../../lib/supabase'

const PAGE_SIZE = 20

export default function PlatformDispatches() {
  const config = usePlatform()

  const [dispatches, setDispatches] = useState([])
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(0)
  const [loading, setLoading] = useState(true)
  const [expanded, setExpanded] = useState(null)

  const loadPage = useCallback(async (p) => {
    setLoading(true)
    const from = p * PAGE_SIZE
    const { data, count, error } = await supabase
      .from(config.tables.dispatches)
      .select('*', { count: 'exact' })
      .eq('platform', config.slug)
      .order('created_at', { ascending: false })
      .range(from, from + PAGE_SIZE - 1)

    if (!error) {
      setDispatches(data || [])
      setTotal(count || 0)
      setPage(p)
    }
    setLoading(false)
  }, [config])

  useEffect(() => { loadPage(0) }, [loadPage])

  // Realtime
  useEffect(() => {
    const channel = supabase
      .channel(`dispatches-${config.slug}`)
      .on('postgres_changes', { event: '*', schema: 'public', table: config.tables.dispatches }, () => {
        loadPage(page)
      })
      .subscribe()
    return () => supabase.removeChannel(channel)
  }, [config, page, loadPage])

  const totalPages = Math.ceil(total / PAGE_SIZE)

  return (
    <>
      <div className="plat-page-header">
        <h1>Dispatch History</h1>
        <p>{total} total dispatches for {config.name}</p>
      </div>
      <div className="plat-content">
        <div className="card">
          {loading ? (
            <div className="table-status"><div className="loader" /> Loading...</div>
          ) : dispatches.length === 0 ? (
            <div className="table-status">No dispatches yet</div>
          ) : (
            <>
              <div className="table-wrapper">
                <table className="data-table">
                  <thead>
                    <tr>
                      <th>#</th>
                      <th>Date</th>
                      <th>Truck</th>
                      <th>Vehicle</th>
                      <th>Driver</th>
                      <th>Load</th>
                      <th>Fill</th>
                      <th>POs</th>
                      <th>Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {dispatches.map((d, i) => (
                      <>
                        <tr
                          key={d.id}
                          style={{ cursor: 'pointer' }}
                          onClick={() => setExpanded(expanded === d.id ? null : d.id)}
                        >
                          <td className="row-num">{page * PAGE_SIZE + i + 1}</td>
                          <td>{d.dispatch_date || '-'}</td>
                          <td>{d.truck_type}</td>
                          <td>{d.vehicle_number || '-'}</td>
                          <td>{d.driver_name || '-'}</td>
                          <td>{d.loaded_kg?.toLocaleString() || 0} kg</td>
                          <td>{d.fill_percentage?.toFixed(1) || 0}%</td>
                          <td>{(d.po_details || []).length}</td>
                          <td><span className={`plat-status ${d.status}`}>{d.status}</span></td>
                        </tr>
                        {expanded === d.id && (
                          <tr key={`${d.id}-details`}>
                            <td colSpan={9} style={{ background: '#f8f9fc', padding: '14px 20px' }}>
                              <div style={{ fontSize: '12px', color: '#636e72' }}>
                                <strong>Time:</strong> {d.dispatch_time || '-'} |
                                <strong> Phone:</strong> {d.driver_phone || '-'} |
                                <strong> Notes:</strong> {d.notes || '-'}
                              </div>
                              {(d.po_details || []).length > 0 && (
                                <div style={{ marginTop: '10px' }}>
                                  <strong style={{ fontSize: '12px', color: '#636e72' }}>Loaded POs:</strong>
                                  {d.po_details.map((po, j) => (
                                    <div key={j} style={{ fontSize: '12px', padding: '4px 0', color: '#636e72' }}>
                                      {po.po_name} &mdash; {po.weight_kg} kg
                                    </div>
                                  ))}
                                </div>
                              )}
                            </td>
                          </tr>
                        )}
                      </>
                    ))}
                  </tbody>
                </table>
              </div>

              {totalPages > 1 && (
                <div className="pagination">
                  <button className="pg-btn" disabled={page === 0} onClick={() => loadPage(0)}>&laquo;</button>
                  <button className="pg-btn" disabled={page === 0} onClick={() => loadPage(page - 1)}>&lsaquo;</button>
                  <span className="pg-info">{page + 1} / {totalPages}<span className="pg-total"> &middot; {total} dispatches</span></span>
                  <button className="pg-btn" disabled={page >= totalPages - 1} onClick={() => loadPage(page + 1)}>&rsaquo;</button>
                  <button className="pg-btn" disabled={page >= totalPages - 1} onClick={() => loadPage(totalPages - 1)}>&raquo;</button>
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </>
  )
}
