export const useFormatDate = () => {
  const formatDate = (dateStr: string | Date | undefined) => {
    if (!dateStr) return ''
    const d = new Date(dateStr)
    if (isNaN(d.getTime())) {
      // Fallback to current date or return empty if requested
      const now = new Date()
      return now.toLocaleDateString('en-US', { 
        month: 'short', 
        day: 'numeric', 
        hour: '2-digit', 
        minute: '2-digit',
        timeZoneName: 'short'
      })
    }
    return d.toLocaleDateString('en-US', { 
      month: 'short', 
      day: 'numeric', 
      hour: '2-digit', 
      minute: '2-digit',
      timeZoneName: 'short'
    })
  }

  const formatTimeOnly = (dateStr: string | Date | undefined) => {
    if (!dateStr) return ''
    const d = new Date(dateStr)
    return d.toLocaleTimeString('en-US', { 
      hour: '2-digit', 
      minute: '2-digit',
      timeZoneName: 'short'
    })
  }

  return {
    formatDate,
    formatTimeOnly
  }
}
