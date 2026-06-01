import { BrowserRouter, Route, Routes } from 'react-router-dom'
import HomePage from './pages/HomePage'
import SignInPage from './pages/SignInPage'
import SignUpPage from './pages/SignUpPage'
import ResultsPage from './pages/ResultsPage'
import ProvidersPage from './pages/ProvidersPage'
import PortfolioPage from './pages/PortfolioPage'
import PlanFinderPage from './pages/PlanFinderPage'
import PlanDetailsPage from './pages/PlanDetailsPage'
import OffersPage from './pages/OffersPage'
import MyPlanPage from './pages/MyPlanPage'
import DashboardPage from './pages/DashboardPage'
import ConfirmationPage from './pages/ConfirmationPage'
import CheckoutPage from './pages/CheckoutPage'
import Verify2FAPage from './pages/Verify2FAPage'
export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/signin" element={<SignInPage />} />
        <Route path="/signup" element={<SignUpPage />} />
        <Route path="/results" element={<ResultsPage />} />
        <Route path="/providers" element={<ProvidersPage />} />
        <Route path="/my-portfolio" element={<PortfolioPage />} />
        <Route path="/plan-finder" element={<PlanFinderPage />} />
        <Route path="/plan-details/:planId" element={<PlanDetailsPage />} />
        <Route path="/offers" element={<OffersPage />} />
        <Route path="/my-plan" element={<MyPlanPage />} />
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="/confirmation" element={<ConfirmationPage />} />
        <Route path="/checkout" element={<CheckoutPage />} />
        <Route path="/verify-2fa" element={<Verify2FAPage />} />
      </Routes>

    </BrowserRouter>
  )
}