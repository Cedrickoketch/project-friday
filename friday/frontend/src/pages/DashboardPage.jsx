import { useState } from 'react'
import TopBar from '../components/dashboard/TopBar'
import NewsPanel from '../components/news/NewsPanel'
import TasksPanel from '../components/tasks/TasksPanel'
import CalendarPanel from '../components/calendar/CalendarPanel'
import FridayLogo from '../components/dashboard/FridayLogo'
import ChatDrawer from '../components/chat/ChatDrawer'
import { useChatStore } from '../store/chatStore'

export default function DashboardPage() {
  const { toggle } = useChatStore()

  return (
    <div className="min-h-screen flex flex-col bg-gray-950">
      <TopBar />

      {/* Main 3-column grid */}
      <main className="flex-1 grid grid-cols-1 lg:grid-cols-3 gap-4 p-4 max-w-screen-2xl mx-auto w-full">
        {/* Left — News */}
        <section className="lg:col-span-1 flex flex-col gap-4">
          <NewsPanel />
        </section>

        {/* Centre — Logo (click to open chat) + Calendar */}
        <section className="lg:col-span-1 flex flex-col items-center gap-4">
          <FridayLogo onClick={toggle} />
          <CalendarPanel />
        </section>

        {/* Right — Tasks */}
        <section className="lg:col-span-1 flex flex-col gap-4">
          <TasksPanel />
        </section>
      </main>

      {/* Chat drawer — slides in from the bottom */}
      <ChatDrawer />
    </div>
  )
}
