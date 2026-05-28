import { createContext, useContext, useState, useCallback, useRef } from 'react'
import { platformAPI } from '../lib/api'

const DispatchContext = createContext(null)

export function DispatchProvider({ children }) {
  // { [slug]: { data: [], loading: bool, error: string|null } }
  const [byPlatform, setByPlatform] = useState({})
  const inflight = useRef({})

  const loadByPlatform = useCallback(async (slug) => {
    if (!slug) return
    if (inflight.current[slug]) return inflight.current[slug]

    setByPlatform((prev) => ({
      ...prev,
      [slug]: { ...(prev[slug] || { data: [] }), loading: true, error: null },
    }))

    const promise = platformAPI
      .listDispatches(slug)
      .then((res) => {
        setByPlatform((prev) => ({
          ...prev,
          [slug]: { data: res.data || [], loading: false, error: null },
        }))
      })
      .catch((err) => {
        setByPlatform((prev) => ({
          ...prev,
          [slug]: { data: prev[slug]?.data || [], loading: false, error: err.message },
        }))
      })
      .finally(() => { delete inflight.current[slug] })

    inflight.current[slug] = promise
    return promise
  }, [])

  const getByPlatform = useCallback((slug) => {
    return byPlatform[slug]?.data || []
  }, [byPlatform])

  const getState = useCallback((slug) => {
    return byPlatform[slug] || { data: [], loading: false, error: null }
  }, [byPlatform])

  const addDispatch = useCallback(async (entry) => {
    const slug = entry.platform_slug
    if (!slug) throw new Error('platform_slug is required')
    const created = await platformAPI.createDispatch(slug, entry)
    setByPlatform((prev) => ({
      ...prev,
      [slug]: {
        data: [created, ...(prev[slug]?.data || [])],
        loading: false,
        error: null,
      },
    }))
    return created
  }, [])

  const deleteDispatch = useCallback(async (id, slug) => {
    if (!slug) throw new Error('slug is required to delete a dispatch')
    await platformAPI.deleteDispatch(slug, id)
    setByPlatform((prev) => ({
      ...prev,
      [slug]: {
        data: (prev[slug]?.data || []).filter((d) => String(d.id) !== String(id)),
        loading: false,
        error: null,
      },
    }))
  }, [])

  const clearAll = useCallback(async (slug) => {
    if (!slug) return
    await platformAPI.clearDispatches(slug)
    setByPlatform((prev) => ({
      ...prev,
      [slug]: { data: [], loading: false, error: null },
    }))
  }, [])

  return (
    <DispatchContext.Provider value={{
      loadByPlatform,
      getByPlatform,
      getState,
      addDispatch,
      deleteDispatch,
      clearAll,
    }}>
      {children}
    </DispatchContext.Provider>
  )
}

export const useDispatch = () => useContext(DispatchContext)
