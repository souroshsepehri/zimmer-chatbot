'use client'

import { useState } from 'react'

export default function SimpleInputTest() {
  const [text, setText] = useState('')

  return (
    <div className="fixed top-4 left-4 bg-white p-4 rounded-lg shadow-lg border z-50">
      <h3 className="text-lg font-bold mb-2">Input Test</h3>
      <input
        type="text"
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder="Type here to test..."
        className="w-full px-3 py-2 border border-gray-300 rounded mb-2"
      />
      <p className="text-sm text-gray-600">Current value: &quot;{text}&quot;</p>
    </div>
  )
}







