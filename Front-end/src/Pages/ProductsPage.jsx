// Add this console log to debug the API call
const fetchProducts = async () => {
  try {
    console.log("Fetching products from:", "http://localhost:5000/products");
    const response = await axios.get("http://localhost:5000/products");
    console.log("Products response:", response.data);
    // Rest of your code...
  } catch (error) {
    console.error("Error fetching products:", error);
    // Rest of your error handling...
  }
};