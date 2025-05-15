import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { toast } from 'react-toastify';
import { useNavigate } from 'react-router-dom';
import { FaEdit, FaTrash, FaUserPlus, FaSearch } from 'react-icons/fa';
import { FiRefreshCw } from 'react-icons/fi';
import AdminNav from '../../../Components/AdminNav/AdminNav';
import styles from './AdminUsers.module.css';

const AdminUsers = () => {
    const [users, setUsers] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [searchTerm, setSearchTerm] = useState('');
    const [showModal, setShowModal] = useState(false);
    const [editingUser, setEditingUser] = useState(null);
    const [formData, setFormData] = useState({
        username: '',
        email: '',
        full_name: '',
        user_address: '',
        phone_number: '',
        user_role: 'Customer',
        password: ''
    });
    const navigate = useNavigate();

    const fetchUsers = async () => {
        setLoading(true);
        setError(null);

        try {
            const token = localStorage.getItem('token');
            
            if (!token) {
                toast.error('Authentication required');
                navigate('/signin');
                return;
            }

            const response = await axios.get('http://localhost:5000/admin/users', {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            setUsers(response.data.users);
        } catch (err) {
            console.error('Error fetching users:', err);
            setError('Failed to load users. Please try again later.');
            
            if (err.response && (err.response.status === 401 || err.response.status === 403)) {
                toast.error('You are not authorized to access this page');
                navigate('/signin');
            }
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchUsers();
    }, [navigate]);

    const handleSearchChange = (e) => {
        setSearchTerm(e.target.value);
    };

    const filteredUsers = users.filter(user => {
        const searchString = searchTerm.toLowerCase();
        return (
            user.username.toLowerCase().includes(searchString) ||
            user.email.toLowerCase().includes(searchString) ||
            user.full_name.toLowerCase().includes(searchString) ||
            (user.user_address && user.user_address.toLowerCase().includes(searchString)) ||
            (user.phone_number && user.phone_number.toLowerCase().includes(searchString))
        );
    });

    const handleAddUser = () => {
        setEditingUser(null);
        setFormData({
            username: '',
            email: '',
            full_name: '',
            user_address: '',
            phone_number: '',
            user_role: 'Customer',
            password: ''
        });
        setShowModal(true);
    };

    const handleEditUser = (user) => {
        setEditingUser(user);
        setFormData({
            username: user.username,
            email: user.email,
            full_name: user.full_name,
            user_address: user.user_address || '',
            phone_number: user.phone_number || '',
            user_role: user.user_role,
            password: '' // Don't populate password for security
        });
        setShowModal(true);
    };

    const handleDeleteUser = async (userId, username) => {
        if (!window.confirm(`Are you sure you want to delete user ${username}? This action cannot be undone.`)) {
            return;
        }

        try {
            const token = localStorage.getItem('token');
            
            const response = await axios.delete(`http://localhost:5000/admin/user/delete/${userId}`, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            toast.success(`User ${username} deleted successfully`);
            setUsers(users.filter(user => user.id !== userId));
        } catch (err) {
            console.error('Error deleting user:', err);
            
            // Enhanced error handling to show more details
            if (err.response) {
                // The request was made and the server responded with a status code
                // that falls out of the range of 2xx
                console.error('Error response data:', err.response.data);
                console.error('Error response status:', err.response.status);
                
                if (err.response.data && err.response.data.error) {
                    toast.error(`Failed to delete user: ${err.response.data.error}`);
                } else if (err.response.data && err.response.data.message) {
                    toast.error(err.response.data.message);
                } else {
                    toast.error(`Failed to delete user: Server error (${err.response.status})`);
                }
            } else if (err.request) {
                // The request was made but no response was received
                console.error('Error request:', err.request);
                toast.error('Failed to delete user: No response from server');
            } else {
                // Something happened in setting up the request
                toast.error('Failed to delete user: ' + err.message);
            }
        }
    };

    const handleInputChange = (e) => {
        const { name, value } = e.target;
        setFormData({
            ...formData,
            [name]: value
        });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        
        // Basic validation
        if (!formData.username || !formData.email || !formData.full_name) {
            toast.error('Please fill in all required fields');
            return;
        }

        try {
            const token = localStorage.getItem('token');
            
            if (editingUser) {
                // Update existing user
                await axios.put(
                    `http://localhost:5000/admin/user/update/${editingUser.id}`,
                    formData,
                    {
                        headers: {
                            'Authorization': `Bearer ${token}`
                        }
                    }
                );

                toast.success(`User ${formData.username} updated successfully`);
                
                // Update the user in the state
                setUsers(users.map(user => 
                    user.id === editingUser.id ? { ...user, ...formData } : user
                ));
            } else {
                // Add new user
                const response = await axios.post(
                    'http://localhost:5000/admin/user/create',
                    formData,
                    {
                        headers: {
                            'Authorization': `Bearer ${token}`
                        }
                    }
                );

                toast.success(`User ${formData.username} created successfully`);
                
                // Add the new user to the state
                setUsers([...users, response.data]);
            }
            
            setShowModal(false);
        } catch (err) {
            console.error('Error saving user:', err);
            
            if (err.response && err.response.data && err.response.data.message) {
                toast.error(err.response.data.message);
            } else {
                toast.error('Failed to save user');
            }
        }
    };

    return (
        <div className={styles.adminLayout}>
            <AdminNav />
            <div className={styles.dashboardContainer}>
                <div className={styles.dashboardHeader}>
                    <h1>User Management</h1>
                    <div className={styles.headerActions}>
                        <button 
                            className={styles.refreshButton}
                            onClick={fetchUsers}
                            disabled={loading}
                        >
                            <FiRefreshCw className={loading ? styles.spinning : ''} />
                            Refresh
                        </button>
                        <button 
                            className={styles.addButton}
                            onClick={handleAddUser}
                        >
                            <FaUserPlus />
                            Add User
                        </button>
                    </div>
                </div>

                {error && (
                    <div className={styles.error}>
                        <p>{error}</p>
                        <button 
                            className={styles.retryButton}
                            onClick={fetchUsers}
                        >
                            Retry
                        </button>
                    </div>
                )}

                <div className={styles.searchContainer}>
                    <div className={styles.searchBox}>
                        <FaSearch className={styles.searchIcon} />
                        <input
                            type="text"
                            placeholder="Search users..."
                            value={searchTerm}
                            onChange={handleSearchChange}
                            className={styles.searchInput}
                        />
                    </div>
                </div>

                {loading ? (
                    <div className={styles.loadingContainer}>
                        <div className={styles.spinner}></div>
                        <p>Loading users...</p>
                    </div>
                ) : (
                    <>
                        {filteredUsers.length === 0 ? (
                            <div className={styles.noResults}>
                                <p>No users found</p>
                            </div>
                        ) : (
                            <div className={styles.tableContainer}>
                                <table className={styles.usersTable}>
                                    <thead>
                                        <tr>
                                            <th>ID</th>
                                            <th>Username</th>
                                            <th>Email</th>
                                            <th>Full Name</th>
                                            <th>Role</th>
                                            <th>Actions</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {filteredUsers.map(user => (
                                            <tr key={user.id}>
                                                <td>{user.id}</td>
                                                <td>{user.username}</td>
                                                <td>{user.email}</td>
                                                <td>{user.full_name}</td>
                                                <td>
                                                    <span className={`${styles.roleTag} ${user.user_role === 'Admin' ? styles.adminRole : styles.customerRole}`}>
                                                        {user.user_role}
                                                    </span>
                                                </td>
                                                <td className={styles.actions}>
                                                    <button 
                                                        className={styles.editButton}
                                                        onClick={() => handleEditUser(user)}
                                                        title="Edit user"
                                                    >
                                                        <FaEdit />
                                                    </button>
                                                    <button 
                                                        className={styles.deleteButton}
                                                        onClick={() => handleDeleteUser(user.id, user.username)}
                                                        title="Delete user"
                                                        disabled={user.user_role === 'Admin'}
                                                    >
                                                        <FaTrash />
                                                    </button>
                                                </td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>
                        )}
                    </>
                )}
            </div>

            {showModal && (
                <div className={styles.modalOverlay}>
                    <div className={styles.modal}>
                        <div className={styles.modalHeader}>
                            <h2>{editingUser ? 'Edit User' : 'Add New User'}</h2>
                            <button 
                                className={styles.closeButton}
                                onClick={() => setShowModal(false)}
                            >
                                &times;
                            </button>
                        </div>
                        <form onSubmit={handleSubmit} className={styles.userForm}>
                            <div className={styles.formGroup}>
                                <label htmlFor="username">Username *</label>
                                <input
                                    type="text"
                                    id="username"
                                    name="username"
                                    value={formData.username}
                                    onChange={handleInputChange}
                                    required
                                />
                            </div>
                            
                            <div className={styles.formGroup}>
                                <label htmlFor="email">Email *</label>
                                <input
                                    type="email"
                                    id="email"
                                    name="email"
                                    value={formData.email}
                                    onChange={handleInputChange}
                                    required
                                />
                            </div>
                            
                            <div className={styles.formGroup}>
                                <label htmlFor="full_name">Full Name *</label>
                                <input
                                    type="text"
                                    id="full_name"
                                    name="full_name"
                                    value={formData.full_name}
                                    onChange={handleInputChange}
                                    required
                                />
                            </div>
                            
                            <div className={styles.formGroup}>
                                <label htmlFor="user_address">Address</label>
                                <textarea
                                    id="user_address"
                                    name="user_address"
                                    value={formData.user_address}
                                    onChange={handleInputChange}
                                    rows="3"
                                />
                            </div>
                            
                            <div className={styles.formGroup}>
                                <label htmlFor="phone_number">Phone Number</label>
                                <input
                                    type="text"
                                    id="phone_number"
                                    name="phone_number"
                                    value={formData.phone_number}
                                    onChange={handleInputChange}
                                />
                            </div>
                            
                            <div className={styles.formGroup}>
                                <label htmlFor="user_role">Role</label>
                                <select
                                    id="user_role"
                                    name="user_role"
                                    value={formData.user_role}
                                    onChange={handleInputChange}
                                >
                                    <option value="Customer">Customer</option>
                                    <option value="Admin">Admin</option>
                                </select>
                            </div>
                            
                            <div className={styles.formGroup}>
                                <label htmlFor="password">
                                    {editingUser ? 'Password (leave blank to keep current)' : 'Password *'}
                                </label>
                                <input
                                    type="password"
                                    id="password"
                                    name="password"
                                    value={formData.password}
                                    onChange={handleInputChange}
                                    required={!editingUser}
                                />
                            </div>
                            
                            <div className={styles.formActions}>
                                <button 
                                    type="button" 
                                    className={styles.cancelButton}
                                    onClick={() => setShowModal(false)}
                                >
                                    Cancel
                                </button>
                                <button 
                                    type="submit" 
                                    className={styles.saveButton}
                                >
                                    {editingUser ? 'Update User' : 'Add User'}
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}
        </div>
    );
};

export default AdminUsers;







