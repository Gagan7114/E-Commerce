import { useEffect, useState } from 'react'
import { usePlatform } from '../../context/PlatformContext'
import { useAuth } from '../../context/AuthContext'
import { supabase } from '../../lib/supabase'

export default function PlatformTruckLoading() {
  const config = usePlatform()
  const { user } = useAuth()

  const [step, setStep] = useState('select') // select | loading | dispatch
  const [truckType, setTruckType] = useState(null)
  const [session, setSession] = useState(null)
  const [loadedPOs, setLoadedPOs] = useState([])
  const [totalWeight, setTotalWeight] = useState(0)

  // Available POs
  const [availablePOs, setAvailablePOs] = useState([])
  const [poLoading, setPOLoading] = useState(false)

  // Dispatch form
  const [dispatchForm, setDispatchForm] = useState({
    dispatch_date: new Date().toISOString().split('T')[0],
    dispatch_time: '',
    vehicle_number: '',
    driver_name: '',
    driver_phone: '',
    notes: '',
  })
  const [saving, setSaving] = useState(false)

  // Check for existing loading session
  useEffect(() => {
    supabase
      .from(config.tables.dispatches)
      .select('*')
      .eq('platform', config.slug)
      .eq('status', 'loading')
      .order('created_at', { ascending: false })
      .range(0, 0)
      .then(({ data }) => {
        if (data && data.length > 0) {
          const s = data[0]
          setSession(s)
          setTruckType(config.truckTypes.find((t) => t.label === s.truck_type) || config.truckTypes[0])
          setLoadedPOs(s.po_details || [])
          setTotalWeight(s.loaded_kg || 0)
          setStep('loading')
        }
      })
  }, [config])

  // Load available POs
  useEffect(() => {
    if (step !== 'loading') return
    setPOLoading(true)
    supabase
      .from(config.tables.masterPO)
      .select('*')
      .eq(config.poFilterColumn, config.poFilterValue)
      .range(0, 49)
      .then(({ data }) => {
        setAvailablePOs(data || [])
        setPOLoading(false)
      })
  }, [step, config])

  const capacity = truckType?.capacityKg || 0
  const fillPct = capacity > 0 ? Math.min((totalWeight / capacity) * 100, 100) : 0
  const fillColor = fillPct < 70 ? 'green' : fillPct < 90 ? 'yellow' : 'red'

  const poColumns = availablePOs.length > 0 ? Object.keys(availablePOs[0]) : []
  const poNameCol = poColumns.find((c) => /po_number|po_no|po_id|order/i.test(c)) || poColumns[0]

  // Create new truck session
  const createSession = async () => {
    if (!truckType) return
    const { data, error } = await supabase.from(config.tables.dispatches).insert({
      platform: config.slug,
      truck_type: truckType.label,
      capacity_kg: truckType.capacityKg,
      loaded_kg: 0,
      fill_percentage: 0,
      status: 'loading',
      po_details: [],
      created_by: user?.id,
    }).select().single()

    if (!error && data) {
      setSession(data)
      setStep('loading')
    }
  }

  // Add PO to truck
  const addPOToTruck = async (po) => {
    const weight = Number(po[config.weightColumn]) || 0
    const poEntry = {
      po_id: po.id,
      po_name: po[poNameCol] || 'Unknown PO',
      weight_kg: weight,
    }
    const newLoaded = [...loadedPOs, poEntry]
    const newWeight = totalWeight + weight
    const newPct = capacity > 0 ? Math.min((newWeight / capacity) * 100, 100) : 0

    setLoadedPOs(newLoaded)
    setTotalWeight(newWeight)

    if (session) {
      await supabase.from(config.tables.dispatches).update({
        po_details: newLoaded,
        loaded_kg: newWeight,
        fill_percentage: Math.round(newPct * 100) / 100,
      }).eq('id', session.id)
    }
  }

  // Remove PO from truck
  const removePO = async (index) => {
    const removed = loadedPOs[index]
    const newLoaded = loadedPOs.filter((_, i) => i !== index)
    const newWeight = totalWeight - (removed.weight_kg || 0)
    const newPct = capacity > 0 ? Math.min((newWeight / capacity) * 100, 100) : 0

    setLoadedPOs(newLoaded)
    setTotalWeight(newWeight)

    if (session) {
      await supabase.from(config.tables.dispatches).update({
        po_details: newLoaded,
        loaded_kg: newWeight,
        fill_percentage: Math.round(newPct * 100) / 100,
      }).eq('id', session.id)
    }
  }

  // Complete dispatch
  const completeDispatch = async () => {
    if (!session) return
    setSaving(true)
    await supabase.from(config.tables.dispatches).update({
      ...dispatchForm,
      status: 'dispatched',
      fill_percentage: Math.round(fillPct * 100) / 100,
    }).eq('id', session.id)

    setSaving(false)
    setSession(null)
    setLoadedPOs([])
    setTotalWeight(0)
    setStep('select')
    setTruckType(null)
    setDispatchForm({
      dispatch_date: new Date().toISOString().split('T')[0],
      dispatch_time: '',
      vehicle_number: '',
      driver_name: '',
      driver_phone: '',
      notes: '',
    })
  }

  return (
    <>
      <div className="plat-page-header">
        <h1>Truck Loading</h1>
        <p>Load POs into trucks and dispatch</p>
      </div>
      <div className="plat-content">

        {/* Step 1: Select truck */}
        {step === 'select' && (
          <div className="plat-truck-section">
            <h3>Select Truck Type</h3>
            <div className="plat-truck-types">
              {config.truckTypes.map((t) => (
                <button
                  key={t.label}
                  className={`plat-truck-type-btn ${truckType?.label === t.label ? 'selected' : ''}`}
                  onClick={() => setTruckType(t)}
                >
                  <span className="plat-truck-type-label">{t.label}</span>
                  <span className="plat-truck-type-cap">{t.capacityKg.toLocaleString()} kg capacity</span>
                </button>
              ))}
            </div>
            <button
              className="plat-btn plat-btn-primary"
              disabled={!truckType}
              onClick={createSession}
            >
              Start Loading
            </button>
          </div>
        )}

        {/* Step 2: Loading */}
        {step === 'loading' && (
          <>
            {/* Fill bar */}
            <div className="plat-truck-section">
              <h3>Truck: {truckType?.label}</h3>
              <div className="plat-truck-fill">
                <div className="plat-truck-fill-header">
                  <span>{totalWeight.toLocaleString()} / {capacity.toLocaleString()} kg</span>
                  <span className="plat-truck-fill-pct">{fillPct.toFixed(1)}%</span>
                </div>
                <div className="plat-truck-fill-bar">
                  <div
                    className={`plat-truck-fill-progress ${fillColor}`}
                    style={{ width: `${fillPct}%` }}
                  />
                </div>
              </div>

              {/* Loaded POs */}
              {loadedPOs.length > 0 && (
                <>
                  <h4 style={{ fontSize: '13px', fontWeight: 600, color: '#636e72', marginBottom: '10px' }}>
                    Loaded POs ({loadedPOs.length})
                  </h4>
                  {loadedPOs.map((po, i) => (
                    <div key={i} className="plat-loaded-item">
                      <div className="plat-truck-po-info">
                        <div className="plat-truck-po-name">{po.po_name}</div>
                        <div className="plat-truck-po-weight">{po.weight_kg} kg</div>
                      </div>
                      <button className="plat-loaded-remove" onClick={() => removePO(i)}>Remove</button>
                    </div>
                  ))}
                </>
              )}

              <div style={{ display: 'flex', gap: '10px', marginTop: '16px' }}>
                <button className="plat-btn plat-btn-primary" onClick={() => setStep('dispatch')} disabled={loadedPOs.length === 0}>
                  Complete Loading
                </button>
                <button className="plat-btn plat-btn-secondary" onClick={() => { setStep('select'); setSession(null); setLoadedPOs([]); setTotalWeight(0) }}>
                  Cancel
                </button>
              </div>
            </div>

            {/* Available POs */}
            <div className="plat-truck-section">
              <h3>Add POs to Truck</h3>
              {poLoading ? (
                <div className="plat-empty"><div className="loader" /> Loading POs...</div>
              ) : availablePOs.length === 0 ? (
                <div className="plat-empty">No POs available</div>
              ) : (
                availablePOs.map((po, i) => {
                  const alreadyLoaded = loadedPOs.some((l) => l.po_id === po.id)
                  const weight = Number(po[config.weightColumn]) || 0
                  return (
                    <div key={po.id ?? i} className="plat-truck-po-item">
                      <div className="plat-truck-po-info">
                        <div className="plat-truck-po-name">{po[poNameCol] || `PO #${i + 1}`}</div>
                        <div className="plat-truck-po-weight">{weight} {po[config.unitColumn] || 'kg'}</div>
                      </div>
                      <div className="plat-truck-po-actions">
                        {alreadyLoaded ? (
                          <span className="plat-status dispatched">Added</span>
                        ) : (
                          <button className="plat-btn-add" onClick={() => addPOToTruck(po)}>+ Add</button>
                        )}
                      </div>
                    </div>
                  )
                })
              )}
            </div>
          </>
        )}

        {/* Step 3: Dispatch details */}
        {step === 'dispatch' && (
          <div className="plat-truck-section">
            <h3>Dispatch Details</h3>
            <p style={{ fontSize: '13px', color: '#95a5a6', marginBottom: '16px' }}>
              Truck: {truckType?.label} | {loadedPOs.length} POs | {totalWeight.toLocaleString()} kg ({fillPct.toFixed(1)}% full)
            </p>
            <div className="plat-dispatch-form">
              <div className="plat-form-group">
                <label>Dispatch Date</label>
                <input type="date" value={dispatchForm.dispatch_date}
                  onChange={(e) => setDispatchForm({ ...dispatchForm, dispatch_date: e.target.value })} />
              </div>
              <div className="plat-form-group">
                <label>Dispatch Time</label>
                <input type="time" value={dispatchForm.dispatch_time}
                  onChange={(e) => setDispatchForm({ ...dispatchForm, dispatch_time: e.target.value })} />
              </div>
              <div className="plat-form-group">
                <label>Vehicle Number</label>
                <input type="text" placeholder="e.g. MH 12 AB 1234" value={dispatchForm.vehicle_number}
                  onChange={(e) => setDispatchForm({ ...dispatchForm, vehicle_number: e.target.value })} />
              </div>
              <div className="plat-form-group">
                <label>Driver Name</label>
                <input type="text" placeholder="Driver name" value={dispatchForm.driver_name}
                  onChange={(e) => setDispatchForm({ ...dispatchForm, driver_name: e.target.value })} />
              </div>
              <div className="plat-form-group">
                <label>Driver Phone</label>
                <input type="text" placeholder="Phone number" value={dispatchForm.driver_phone}
                  onChange={(e) => setDispatchForm({ ...dispatchForm, driver_phone: e.target.value })} />
              </div>
              <div className="plat-form-group full">
                <label>Notes</label>
                <textarea placeholder="Any additional notes..." value={dispatchForm.notes}
                  onChange={(e) => setDispatchForm({ ...dispatchForm, notes: e.target.value })} />
              </div>
            </div>
            <div style={{ display: 'flex', gap: '10px', marginTop: '18px' }}>
              <button className="plat-btn plat-btn-primary" onClick={completeDispatch} disabled={saving || !dispatchForm.vehicle_number}>
                {saving ? 'Dispatching...' : 'Dispatch Truck'}
              </button>
              <button className="plat-btn plat-btn-secondary" onClick={() => setStep('loading')}>
                Back
              </button>
            </div>
          </div>
        )}

      </div>
    </>
  )
}
