import { useEffect, useState, useCallback, useRef } from 'react'
import { usePlatform } from '../../context/PlatformContext'
import { supabase } from '../../lib/supabase'

const PAGE_SIZE = 50

export default function PlatformPO() {
  const config = usePlatform()

  const [pos, setPOs] = useState([])
  const [poTotal, setPOTotal] = useState(0)
  const [poPage, setPOPage] = useState(0)
  const [poLoading, setPOLoading] = useState(true)
  const [poSearch, setPOSearch] = useState('')
  const searchTimer = useRef(null)
  const [debouncedSearch, setDebouncedSearch] = useState('')

  const [selectedPO, setSelectedPO] = useState(null)
  const [stockMatch, setStockMatch] = useState(null) // matched inventory row
  const [stockLoading, setStockLoading] = useState(false)

  // Debounce search
  const handleSearch = (val) => {
    setPOSearch(val)
    clearTimeout(searchTimer.current)
    searchTimer.current = setTimeout(() => {
      setDebouncedSearch(val)
      setPOPage(0)
    }, 400)
  }

  // Load POs
  const loadPOs = useCallback(async (page, search) => {
    setPOLoading(true)

    let query = supabase
      .from(config.tables.masterPO)
      .select('*', { count: 'exact' })
      .ilike(config.poFilterColumn, config.poFilterValue)

    if (search) {
      query = supabase
        .from(config.tables.masterPO)
        .select('*', { count: 'exact' })
        .ilike(config.poFilterColumn, config.poFilterValue)
        .or(
          `po_number.ilike.%${search}%,` +
          `po_id.ilike.%${search}%,` +
          `order_id.ilike.%${search}%,` +
          `product_name.ilike.%${search}%,` +
          `sku_code.ilike.%${search}%`
        )
    }

    const from = page * PAGE_SIZE
    const { data, count, error } = await query.range(from, from + PAGE_SIZE - 1)

    if (error) {
      const { data: d2, count: c2 } = await supabase
        .from(config.tables.masterPO)
        .select('*', { count: 'exact' })
        .ilike(config.poFilterColumn, config.poFilterValue)
        .range(from, from + PAGE_SIZE - 1)
      setPOs(d2 || [])
      setPOTotal(c2 || 0)
    } else {
      setPOs(data || [])
      setPOTotal(count || 0)
    }
    setPOLoading(false)
  }, [config])

  useEffect(() => {
    loadPOs(poPage, debouncedSearch)
  }, [poPage, debouncedSearch, loadPOs])

  // When PO is selected, fetch matching inventory by sku_code
  useEffect(() => {
    if (!selectedPO) { setStockMatch(null); return }

    const skuValue = selectedPO[config.matchColumn]
    if (!skuValue) { setStockMatch(null); return }

    setStockLoading(true)
    supabase
      .from(config.tables.inventory)
      .select('*')
      .eq(config.matchColumn, skuValue)
      .range(0, 0)
      .then(({ data }) => {
        setStockMatch(data && data.length > 0 ? data[0] : null)
        setStockLoading(false)
      })
  }, [selectedPO, config])

  const poDisplayCols = pos.length > 0 ? Object.keys(pos[0]) : []
  const poNameCol = poDisplayCols.find((c) => /po_number|po_no|po_id|order/i.test(c)) || poDisplayCols[0]
  const poQtyCol = poDisplayCols.find((c) => /qty|quantity|total_order/i.test(c))
  const poDateCol = poDisplayCols.find((c) => /date|created/i.test(c))

  const totalPoPages = Math.ceil(poTotal / PAGE_SIZE)

  // Stock comparison logic
  const poQty = selectedPO && poQtyCol ? Number(selectedPO[poQtyCol]) || 0 : 0
  const invQtyCol = stockMatch ? Object.keys(stockMatch).find((c) => /qty|quantity|stock|available/i.test(c)) : null
  const invQty = invQtyCol ? Number(stockMatch[invQtyCol]) || 0 : 0
  const stockStatus = !stockMatch ? 'none' : invQty >= poQty ? 'sufficient' : invQty > 0 ? 'partial' : 'empty'

  return (
    <>
      <div className="plat-page-header">
        <h1>PO &amp; Stock Management</h1>
        <p>Select a PO and compare with {config.name} inventory by {config.matchColumn.replace(/_/g, ' ')}</p>
      </div>
      <div className="plat-content">
        <div className="plat-po-layout">
          {/* Left: PO List */}
          <div className="plat-po-panel">
            <div className="plat-po-panel-header">
              Purchase Orders ({poTotal.toLocaleString()})
              <input
                type="text"
                placeholder="Search PO or SKU..."
                value={poSearch}
                onChange={(e) => handleSearch(e.target.value)}
                style={{ float: 'right', padding: '4px 10px', border: '1px solid #e0e3e8', borderRadius: '6px', fontSize: '12px', fontFamily: 'inherit' }}
              />
            </div>
            <div className="plat-po-panel-body">
              {poLoading ? (
                <div className="plat-empty"><div className="loader" /> Loading POs...</div>
              ) : pos.length === 0 ? (
                <div className="plat-empty">No POs found</div>
              ) : (
                <>
                  {pos.map((po, i) => (
                    <div
                      key={po.id ?? i}
                      className={`plat-po-item ${selectedPO?.id === po.id ? 'selected' : ''}`}
                      onClick={() => setSelectedPO(po)}
                    >
                      <div className="plat-po-item-title">{po[poNameCol] || `PO #${i + 1}`}</div>
                      <div className="plat-po-item-sub">
                        {po[config.matchColumn] && <span>SKU: {po[config.matchColumn]} </span>}
                        {poQtyCol && <span>Qty: {po[poQtyCol]} </span>}
                        {poDateCol && <span>Date: {po[poDateCol]}</span>}
                      </div>
                    </div>
                  ))}
                  {totalPoPages > 1 && (
                    <div className="pagination" style={{ padding: '10px 0' }}>
                      <button className="pg-btn" disabled={poPage === 0} onClick={() => setPOPage(poPage - 1)}>&lsaquo;</button>
                      <span className="pg-info">{poPage + 1} / {totalPoPages}</span>
                      <button className="pg-btn" disabled={poPage >= totalPoPages - 1} onClick={() => setPOPage(poPage + 1)}>&rsaquo;</button>
                    </div>
                  )}
                </>
              )}
            </div>
          </div>

          {/* Right: Stock Comparison */}
          <div className="plat-po-panel">
            <div className="plat-po-panel-header">
              Stock Comparison
            </div>
            <div className="plat-po-panel-body">
              {!selectedPO ? (
                <div className="plat-empty">Select a PO to compare stock</div>
              ) : stockLoading ? (
                <div className="plat-empty"><div className="loader" /> Checking inventory...</div>
              ) : (
                <>
                  {/* PO Details */}
                  <div style={{ marginBottom: '16px', padding: '14px', background: '#f8f9fc', borderRadius: '10px' }}>
                    <div style={{ fontWeight: 700, fontSize: '15px', marginBottom: '8px', color: '#2d3436' }}>
                      PO: {selectedPO[poNameCol]}
                    </div>
                    <div className="plat-stock-row">
                      <span className="plat-stock-label">SKU Code</span>
                      <span className="plat-stock-val neutral">{selectedPO[config.matchColumn] || 'N/A'}</span>
                    </div>
                    {poQtyCol && (
                      <div className="plat-stock-row">
                        <span className="plat-stock-label">PO Quantity Required</span>
                        <span className="plat-stock-val neutral">{selectedPO[poQtyCol]}</span>
                      </div>
                    )}
                    {poDateCol && (
                      <div className="plat-stock-row">
                        <span className="plat-stock-label">PO Date</span>
                        <span className="plat-stock-val neutral">{selectedPO[poDateCol]}</span>
                      </div>
                    )}
                    {selectedPO.status && (
                      <div className="plat-stock-row">
                        <span className="plat-stock-label">Status</span>
                        <span className="plat-stock-val neutral">{selectedPO.status}</span>
                      </div>
                    )}
                  </div>

                  {/* Comparison Result */}
                  <div className={`plat-comparison-result ${stockStatus}`}>
                    {stockStatus === 'none' ? (
                      <>
                        <div className="plat-comp-icon">&#10060;</div>
                        <div className="plat-comp-text">
                          <strong>No inventory found</strong>
                          <span>SKU {selectedPO[config.matchColumn]} not found in {config.name} inventory</span>
                        </div>
                      </>
                    ) : stockStatus === 'sufficient' ? (
                      <>
                        <div className="plat-comp-icon">&#9989;</div>
                        <div className="plat-comp-text">
                          <strong>Stock Sufficient — Can Fulfill</strong>
                          <span>Available: {invQty} | Required: {poQty} | Surplus: {invQty - poQty}</span>
                        </div>
                      </>
                    ) : stockStatus === 'partial' ? (
                      <>
                        <div className="plat-comp-icon">&#9888;&#65039;</div>
                        <div className="plat-comp-text">
                          <strong>Partial Stock — Short by {poQty - invQty}</strong>
                          <span>Available: {invQty} | Required: {poQty}</span>
                        </div>
                      </>
                    ) : (
                      <>
                        <div className="plat-comp-icon">&#10060;</div>
                        <div className="plat-comp-text">
                          <strong>Out of Stock</strong>
                          <span>Required: {poQty} | Available: 0</span>
                        </div>
                      </>
                    )}
                  </div>

                  {/* Inventory Details */}
                  {stockMatch && (
                    <div style={{ marginTop: '16px', padding: '14px', background: '#f8f9fc', borderRadius: '10px' }}>
                      <div style={{ fontWeight: 600, fontSize: '13px', marginBottom: '8px', color: '#636e72' }}>
                        Inventory Details
                      </div>
                      {Object.entries(stockMatch).map(([key, val]) => (
                        <div key={key} className="plat-stock-row">
                          <span className="plat-stock-label">{key.replace(/_/g, ' ')}</span>
                          <span className="plat-stock-val neutral">
                            {val === null ? 'NULL' : String(val)}
                          </span>
                        </div>
                      ))}
                    </div>
                  )}
                </>
              )}
            </div>
          </div>
        </div>
      </div>
    </>
  )
}
