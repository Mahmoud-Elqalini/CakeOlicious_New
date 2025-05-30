// Shahd Elwan
import { useState, useEffect, Suspense, lazy } from 'react'
import './App.css'
import Layout from './Components/Layout/Layout'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { ToastContainer } from 'react-toastify'
import { AuthProvider } from './context/AuthContext';
const HomePage = lazy(() => import('./Pages/HomePage/HomePage'))
const ProductsPage = lazy(() => import('./Pages/ProductsPage/ProductsPage'))
const NotFound = lazy(() => import('./Pages/NotFound/NotFound'))
const SignIn = lazy(() => import('./Pages/SignIn/SignIn'))
const SignUp = lazy(() => import('./Pages/SignUp/SignUp'))
const AdminDashboard = lazy(() => import('./Pages/Admin/Dashboard'))
const AdminProducts = lazy(() => import('./Pages/Admin/Products/AdminProducts'))
const Account = lazy(() => import('./Pages/Account/Account'))
const Cart = lazy(() => import('./Pages/Cart/Cart'))
const Checkout = lazy(() => import('./Pages/Checkout/Checkout'))
const OrderSuccess = lazy(() => import('./Pages/OrderSuccess/OrderSuccess'))
import ProtectedRoute from './Components/ProtectedRoute/ProtectedRoute'
import ErrorBoundary from './Components/ErrorBoundary/ErrorBoundary'
import AdminUsers from './Pages/Admin/Users/AdminUsers'
const ProductDetail = lazy(() => import('./Pages/ProductDetail/ProductDetail'))
import Wishlist from './Pages/Wishlist/Wishlist';
import ContactUs from './Components/ContactUs/ContactUs'

function App() {
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchHomeData = async () => {
      try {
        const response = await fetch('http://127.0.0.1:5000/');
        if (!response.ok) {
          throw new Error(`HTTP error! Status: ${response.status}`);
        }
        const data = await response.text();
        setMessage(data);
      } catch (err) {
        setError(err.message);
        console.error('Error fetching home data:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchHomeData();
  }, []);

  return (
    <AuthProvider>
      <Router>
        <ErrorBoundary>
          <Routes>
          
          <Route
            path="/admin/dashboard"
            element={
              <ProtectedRoute requiredRole="admin">
                <AdminDashboard />
              </ProtectedRoute>
            }
          />
          <Route
            path="/admin/products"
            element={
              <ProtectedRoute requiredRole="admin">
                <AdminProducts />
              </ProtectedRoute>
            }
          />
          <Route
            path="/admin/users"
            element={
              <ProtectedRoute requiredRole="admin">
                <AdminUsers />
              </ProtectedRoute>
            }
          />

          {}
          <Route path="/" element={
            <Layout>
              <Suspense fallback={<div className="loading-spinner">Loading...</div>}>
                <HomePage />
              </Suspense>
            </Layout>
          } />
          <Route path="/products" element={
            <Layout>
              <Suspense fallback={<div className="loading-spinner">Loading...</div>}>
                <ProductsPage />
              </Suspense>
            </Layout>
          } />
          <Route path="/products/:productId" element={
            <Layout>
              <Suspense fallback={<div className="loading-spinner">Loading...</div>}>
                <ProductDetail />
              </Suspense>
            </Layout>
          } />
          <Route path="/signin" element={
            <Layout>
              <Suspense fallback={<div className="loading-spinner">Loading...</div>}>
                <SignIn />
              </Suspense>
            </Layout>
          } />
          <Route path="/signup" element={
            <Layout>
              <Suspense fallback={<div className="loading-spinner">Loading...</div>}>
                <SignUp />
              </Suspense>
            </Layout>
          } />
          <Route path="/account" element={
            <Layout>
              <Suspense fallback={<div className="loading-spinner">Loading...</div>}>
                <Account />
              </Suspense>
            </Layout>
          } />
          <Route path="/cart" element={
            <Layout>
              <Suspense fallback={<div className="loading-spinner">Loading...</div>}>
                <Cart />
              </Suspense>
            </Layout>
          } />
          <Route path="/checkout" element={
            <Layout>
              <Suspense fallback={<div className="loading-spinner">Loading...</div>}>
                <Checkout />
              </Suspense>
            </Layout>
          } />
          <Route path="/order/success" element={
            <Layout>
              <Suspense fallback={<div className="loading-spinner">Loading...</div>}>
                <OrderSuccess />
              </Suspense>
            </Layout>
          } />
          <Route path="/order/cancel" element={
            <Layout>
              <Suspense fallback={<div className="loading-spinner">Loading...</div>}>
                <NotFound />
              </Suspense>
            </Layout>
          } />
          <Route path="/wishlist" element={
            <Layout>
              <Suspense fallback={<div className="loading-spinner">Loading...</div>}>
                <Wishlist />
              </Suspense>
            </Layout>
          } />
          <Route path="/contact" element={
            <Layout>
              <Suspense fallback={<div className="loading-spinner">Loading...</div>}>
                <ContactUs />
              </Suspense>
            </Layout>
          } />

          {}
          <Route path="*" element={
            <Layout>
              <Suspense fallback={<div className="loading-spinner">Loading...</div>}>
                <NotFound />
              </Suspense>
            </Layout>
          } />
        </Routes>
        </ErrorBoundary>
      </Router>
      <ToastContainer position="top-right" autoClose={3000} />
    </AuthProvider>
  )
}

export default App
