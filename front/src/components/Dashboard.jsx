import { useState, useEffect } from "react";
import ThemeToggle from "./ThemeToggle";
import SalesChart from "./charts/SalesChart";
import SalesTimelineChart from "./charts/SalesTimelineChart";
import StockLevelsChart from "./charts/StockLevelsChart";
import TransactionModal from "./modals/TransactionModal";
import ProductModal from "./modals/ProductModal";
import EditProductModal from "./modals/EditProductModal";
import AIChat from "./AIChat";
import AIAnalysis from "./AIAnalysis";
import StockComparison from "./StockComparison";

const Dashboard = () => {
  const [data, setData] = useState({
    products: [],
    sales: [],
    stock_levels: [],
    summary: {
      total_products: 0,
      total_sales: 0,
      total_revenue: 0,
      low_stock_items: 0,
      sales_by_category: {},
    },
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedTransaction, setSelectedTransaction] = useState(null);
  const [selectedProduct, setSelectedProduct] = useState(null);
  const [editingProduct, setEditingProduct] = useState(null);
  const [aiMessages, setAiMessages] = useState([]);
  const [isAiActive, setIsAiActive] = useState(false);
  const [isAiProcessing, setIsAiProcessing] = useState(false);
  const [aiAnalysis, setAiAnalysis] = useState(null);
  const [isReceivingOrders, setIsReceivingOrders] = useState(false);
  const [virtualStock, setVirtualStock] = useState([]);

  const handleReceiveOrders = async () => {
    setIsReceivingOrders(true);

    setAiMessages((prev) => [
      ...prev,
      {
        type: "system",
        content: "📦 Réception des commandes en cours...",
        time: new Date().toLocaleTimeString(),
      },
    ]);

    try {
      const response = await fetch("http://localhost:8000/api/orders/receive-all-pending", {
        method: "POST",
      });
      const result = await response.json();

      if (result.success) {
        setAiMessages((prev) => [
          ...prev,
          {
            type: "success",
            content: `✅ ${result.message} - Stock mis à jour !`,
            time: new Date().toLocaleTimeString(),
          },
        ]);

        // Afficher les détails des commandes reçues
        if (result.orders && result.orders.length > 0) {
          result.orders.forEach((order) => {
            setAiMessages((prev) => [
              ...prev,
              {
                type: "success",
                content: `📦 ${order.sku}: +${order.quantity} unités → Stock: ${order.new_stock}`,
                time: new Date().toLocaleTimeString(),
              },
            ]);
          });
        }

        // Rafraîchir les données et l'analyse
        await fetchData();

        const analysisResponse = await fetch("http://localhost:8000/api/agent/llm/analysis");
        const analysisData = await analysisResponse.json();
        setAiAnalysis(analysisData);
      }
    } catch (error) {
      console.error("Erreur lors de la réception des commandes:", error);
      setAiMessages((prev) => [
        ...prev,
        {
          type: "error",
          content: `❌ Erreur: ${error.message}`,
          time: new Date().toLocaleTimeString(),
        },
      ]);
    } finally {
      setIsReceivingOrders(false);
    }
  };

  const handleStartAI = async () => {
    setIsAiActive(true);
    setIsAiProcessing(true);
    setAiAnalysis(null); // Reset l'analyse précédente

    setAiMessages((prev) => [
      ...prev,
      {
        type: "system",
        content: "🤖 Assistant IA Gemini activé - Analyse en cours...",
        time: new Date().toLocaleTimeString(),
      },
    ]);

    try {
      // Appel au service LLM Gemini via le backend (proxy)
      const response = await fetch("http://localhost:8000/api/agent/llm/query");
      const result = await response.json();

      setAiMessages((prev) => [
        ...prev,
        {
          type: "ai",
          content: `✅ ${result.response}`,
          time: new Date().toLocaleTimeString(),
        },
      ]);

      // Attendre que l'agent traite les requêtes (15 secondes)
      setTimeout(async () => {
        try {
          // Récupérer l'analyse structurée
          const analysisResponse = await fetch("http://localhost:8000/api/agent/llm/analysis");
          const analysisData = await analysisResponse.json();

          setAiAnalysis(analysisData);

          // Récupérer aussi l'historique pour afficher les messages
          const historyResponse = await fetch("http://localhost:8000/api/agent/llm/history");
          const history = await historyResponse.json();

          if (history.history && history.history.length > 0) {
            history.history.forEach((item) => {
              setAiMessages((prev) => [
                ...prev,
                {
                  type: "query",
                  content: `❓ ${item.query}`,
                  time: new Date().toLocaleTimeString(),
                },
                {
                  type: "response",
                  content: `🤖 Gemini: ${item.response}`,
                  time: new Date().toLocaleTimeString(),
                },
              ]);
            });
          } else {
            // Si pas d'historique (quota dépassé), afficher quand même l'analyse
            setAiMessages((prev) => [
              ...prev,
              {
                type: "ai",
                content: `🔍 Analyse des données en cours sans IA (quota Gemini atteint)...`,
                time: new Date().toLocaleTimeString(),
              },
            ]);
          }

          const totalProducts = analysisData.summary.total_low_stock;

          setAiMessages((prev) => [
            ...prev,
            {
              type: "success",
              content: `✨ Détection terminée ! ${totalProducts} produit${totalProducts > 1 ? 's' : ''} en rupture de stock détecté${totalProducts > 1 ? 's' : ''}.`,
              time: new Date().toLocaleTimeString(),
            },
          ]);

          // Si des produits en rupture sont détectés, passer les commandes automatiquement
          if (totalProducts > 0) {
            setAiMessages((prev) => [
              ...prev,
              {
                type: "ai",
                content: `🛒 Passage automatique des commandes de réapprovisionnement...`,
                time: new Date().toLocaleTimeString(),
              },
            ]);

            const restockResponse = await fetch("http://localhost:8000/api/agent/llm/auto_restock", {
              method: "POST",
            });
            const restockData = await restockResponse.json();

            if (restockData.success) {
              setAiMessages((prev) => [
                ...prev,
                {
                  type: "success",
                  content: `✅ ${restockData.message}`,
                  time: new Date().toLocaleTimeString(),
                },
              ]);

              // Rafraîchir l'analyse pour afficher les commandes
              const newAnalysisResponse = await fetch("http://localhost:8000/api/agent/llm/analysis");
              const newAnalysisData = await newAnalysisResponse.json();
              setAiAnalysis(newAnalysisData);
            }
          } else {
            setAiMessages((prev) => [
              ...prev,
              {
                type: "success",
                content: `✅ Aucune action requise - Tous les stocks sont à niveau.`,
                time: new Date().toLocaleTimeString(),
              },
            ]);
          }

          // Rafraîchir les données pour voir les commandes créées
          await fetchData();

        } catch (error) {
          console.error("Erreur lors de la récupération de l'analyse:", error);
          setAiMessages((prev) => [
            ...prev,
            {
              type: "error",
              content: `❌ Erreur d'analyse: ${error.message}`,
              time: new Date().toLocaleTimeString(),
            },
          ]);
        } finally {
          setIsAiProcessing(false);
        }
      }, 15000); // Attendre 15 secondes pour que Gemini traite

    } catch (error) {
      console.error("Erreur lors de l'appel à l'IA:", error);
      setAiMessages((prev) => [
        ...prev,
        {
          type: "error",
          content: `❌ Erreur: ${error.message}`,
          time: new Date().toLocaleTimeString(),
        },
      ]);
      setIsAiProcessing(false);
    }
  };

  const handleEditProduct = (product) => {
    setEditingProduct(product);
  };

  const fetchData = async () => {
    try {
      const [productsRes, salesRes, stockRes, virtualStockRes] = await Promise.all([
        fetch("http://localhost:8000/api/products"),
        fetch("http://localhost:8000/api/sales"),
        fetch("http://localhost:8000/api/stocks"),
        fetch("http://localhost:8000/api/stocks/virtual/all"),
      ]);

      const products = await productsRes.json();
      const sales = await salesRes.json();
      const stockLevels = await stockRes.json();
      const virtualStockData = await virtualStockRes.json();

      // Mettre à jour le stock virtuel
      setVirtualStock(virtualStockData);

      // Calculer le résumé des données
      const summary = {
        total_products: products.length,
        total_sales: sales.length,
        total_revenue: sales.reduce((total, sale) => {
          const product = products.find((p) => p.sku === sale.sku);
          return total + (product ? product.price * sale.quantity : 0);
        }, 0),
        low_stock_items: stockLevels.filter((item) => item.stock_on_hand < 50)
          .length,
        sales_by_category: products.reduce((acc, product) => {
          const productSales = sales.filter(
            (sale) => sale.sku === product.sku
          ).length;
          acc[product.category] = (acc[product.category] || 0) + productSales;
          return acc;
        }, {}),
      };

      setData({
        products,
        sales,
        stock_levels: stockLevels,
        summary,
      });
      setError(null);
    } catch (err) {
      setError("Erreur lors du chargement des données");
      console.error("Erreur lors du chargement des données:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
    // Rafraîchir les données toutes les 5 secondes pour voir les mises à jour en temps réel
    const interval = setInterval(fetchData, 5000);
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-base-200">
        <div className="loading loading-spinner loading-lg text-primary"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-base-200">
        <div className="alert alert-error">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            className="stroke-current shrink-0 h-6 w-6"
            fill="none"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="2"
              d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
          <span>{error}</span>
        </div>
      </div>
    );
  }

  return (
    <div className="p-4 min-h-screen bg-base-200">
      <div className="max-w-7xl mx-auto">
        {/* En-tête avec sélecteur de thème */}
        <div className="mb-8 flex justify-between items-center">
          <div>
            <h1 className="text-4xl font-bold text-base-content">Dashboard</h1>
            <div className="text-sm breadcrumbs">
              <ul>
                <li>Dashboard</li>
                <li>Global View</li>
              </ul>
            </div>
          </div>
          <div className="flex gap-4 items-center">
            <button
              className={`btn btn-lg gap-2 ${
                isAiActive
                  ? isAiProcessing
                    ? "btn-warning loading"
                    : "btn-success"
                  : "btn-primary"
              }`}
              onClick={handleStartAI}
              disabled={isAiActive}
            >
              {isAiProcessing ? (
                <>
                  <span className="loading loading-spinner"></span>
                  Traitement en cours...
                </>
              ) : (
                <>
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    fill="none"
                    viewBox="0 0 24 24"
                    strokeWidth={1.5}
                    stroke="currentColor"
                    className="w-6 h-6"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09zM18.259 8.715L18 9.75l-.259-1.035a3.375 3.375 0 00-2.455-2.456L14.25 6l1.036-.259a3.375 3.375 0 002.455-2.456L18 2.25l.259 1.035a3.375 3.375 0 002.456 2.456L21.75 6l-1.035.259a3.375 3.375 0 00-2.456 2.456zM16.894 20.567L16.5 21.75l-.394-1.183a2.25 2.25 0 00-1.423-1.423L13.5 18.75l1.183-.394a2.25 2.25 0 001.423-1.423l.394-1.183.394 1.183a2.25 2.25 0 001.423 1.423l1.183.394-1.183.394a2.25 2.25 0 00-1.423 1.423z"
                    />
                  </svg>
                  {isAiActive ? "IA Active ✓" : "Démarrer l'IA"}
                </>
              )}
            </button>
            <ThemeToggle />
          </div>
        </div>

        {/* Section IA - Chat et Analyse */}
        {isAiActive && (
          <div className="mb-8 space-y-4">
            <AIChat messages={aiMessages} />
            {aiAnalysis && (
              <AIAnalysis
                analysis={aiAnalysis}
                onReceiveOrders={handleReceiveOrders}
                isReceiving={isReceivingOrders}
              />
            )}
            <StockComparison stocks={virtualStock} />
          </div>
        )}

        {/* Cartes de statistiques */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          <div className="stats shadow bg-primary">
            <div className="stat">
              <div className="stat-title text-primary-content opacity-80">
                Products
              </div>
              <div className="stat-value text-primary-content">
                {data.summary.total_products}
              </div>
              <div className="stat-desc text-primary-content opacity-70">
                In sales
              </div>
            </div>
          </div>

          <div className="stats shadow bg-secondary">
            <div className="stat">
              <div className="stat-title text-secondary-content opacity-80">
                Sales
              </div>
              <div className="stat-value text-secondary-content">
                {data.summary.total_sales}
              </div>
              <div className="stat-desc text-secondary-content opacity-70">
                Units sold
              </div>
            </div>
          </div>

          <div className="stats shadow bg-accent">
            <div className="stat">
              <div className="stat-title text-accent-content opacity-80">
                Low Stock
              </div>
              <div className="stat-value text-accent-content">
                {data.summary.low_stock_items}
              </div>
              <div className="stat-desc text-accent-content opacity-70">
                {"< 50 units"}
              </div>
            </div>
          </div>

          <div className="stats shadow bg-neutral">
            <div className="stat">
              <div className="stat-title text-neutral-content opacity-80">
                CA Total
              </div>
              <div className="stat-value text-neutral-content">
                {data.summary.total_revenue.toFixed(2)}€
              </div>
              <div className="stat-desc text-neutral-content opacity-70">
                Revenue
              </div>
            </div>
          </div>
        </div>

        {/* Section des graphiques */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-8">
          <div className="card bg-base-100 shadow-xl">
            <div className="card-body">
              <h2 className="card-title">Sales by category</h2>
              <SalesChart data={data.summary.sales_by_category} />
            </div>
          </div>

          <div className="card bg-base-100 shadow-xl">
            <div className="card-body">
              <h2 className="card-title">Sales trends</h2>
              <SalesTimelineChart sales={data.sales} />
            </div>
          </div>

          <div className="card bg-base-100 shadow-xl lg:col-span-2">
            <div className="card-body">
              <h2 className="card-title">Stock levels</h2>
              <StockLevelsChart
                stockLevels={data.stock_levels}
                products={data.products}
              />
            </div>
          </div>
        </div>

        {/* Tableau des produits */}
        <div className="bg-base-100 rounded-lg shadow-xl overflow-x-auto">
          <table className="table table-zebra w-full">
            <thead>
              <tr>
                <th>SKU</th>
                <th>Name</th>
                <th>Category</th>
                <th>Price</th>
                <th>Stock</th>
                <th>Total sales</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {data.products.map((product) => {
                const stockLevel = data.stock_levels.find(
                  (s) => s.sku === product.sku
                );
                const totalSold = data.sales
                  .filter((s) => s.sku === product.sku)
                  .reduce((sum, sale) => sum + sale.quantity, 0);
                const totalAllSales = data.sales.reduce(
                  (sum, sale) => sum + sale.quantity,
                  0
                );
                const salesPercentage = (
                  (totalSold / totalAllSales) *
                  100
                ).toFixed(1);
                const isLowStock = stockLevel && stockLevel.stock_on_hand < 50;

                return (
                  <tr key={product.sku}>
                    <td>{product.sku}</td>
                    <td>{product.name}</td>
                    <td>
                      <div className="badge badge-ghost text-base-content">
                        {product.category}
                      </div>
                    </td>
                    <td className="font-medium">{product.price.toFixed(2)}€</td>
                    <td>
                      <div
                        className={`badge ${
                          isLowStock
                            ? "badge-error text-error-content"
                            : "badge-success text-success-content"
                        }`}
                      >
                        {stockLevel?.stock_on_hand || 0}
                      </div>
                    </td>
                    <td>
                      <div
                        className="tooltip"
                        data-tip={`${salesPercentage}% des ventes totales`}
                      >
                        <div className="badge badge-neutral text-neutral-content gap-2">
                          {totalSold}
                          <span className="text-xs opacity-70">
                            ({salesPercentage}%)
                          </span>
                        </div>
                      </div>
                    </td>
                    <td>
                      <div className="flex gap-2">
                        <button
                          className="btn btn-sm btn-primary"
                          onClick={() => handleEditProduct(product)}
                        >
                          Edit
                        </button>
                        <button
                          className="btn btn-sm btn-secondary"
                          onClick={() => setSelectedProduct(product)}
                        >
                          Details
                        </button>
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>

        <div className="mt-8 grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="card bg-base-100 shadow-xl">
            <div className="card-body">
              <h2 className="card-title">Top 5 Best-Selling Products</h2>
              <div className="overflow-x-auto">
                <table className="table w-full">
                  <thead>
                    <tr>
                      <th>Product</th>
                      <th>Category</th>
                      <th>Units sold</th>
                      <th>Revenue generated</th>
                    </tr>
                  </thead>
                  <tbody>
                    {data.products
                      .map((product) => {
                        const totalSold = data.sales
                          .filter((s) => s.sku === product.sku)
                          .reduce((sum, sale) => sum + sale.quantity, 0);
                        const revenue = totalSold * product.price;
                        return { ...product, totalSold, revenue };
                      })
                      .sort((a, b) => b.totalSold - a.totalSold)
                      .slice(0, 5)
                      .map((product) => (
                        <tr key={product.sku}>
                          <td>
                            <div className="font-medium">{product.name}</div>
                            <div className="text-sm opacity-50">
                              {product.sku}
                            </div>
                          </td>
                          <td>
                            <div className="badge badge-ghost">
                              {product.category}
                            </div>
                          </td>
                          <td>
                            <div className="badge badge-primary">
                              {product.totalSold}
                            </div>
                          </td>
                          <td>{product.revenue.toFixed(2)}€</td>
                        </tr>
                      ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>

          <div className="card bg-base-100 shadow-xl">
            <div className="card-body">
              <h2 className="card-title">Latest transactions</h2>
              <div className="overflow-x-auto">
                <table className="table table-zebra w-full">
                  <thead>
                    <tr>
                      <th>Transaction</th>
                      <th>Date</th>
                      <th>Quantity</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {data.sales.slice(-5).map((sale) => (
                      <tr key={`${sale.transaction_id}-${sale.sku}`}>
                        <td>{sale.transaction_id}</td>
                        <td>{new Date(sale.timestamp).toLocaleString()}</td>
                        <td>{sale.quantity}</td>
                        <td>
                          <button
                            className="btn btn-sm btn-ghost"
                            onClick={() => setSelectedTransaction(sale)}
                          >
                            <svg
                              xmlns="http://www.w3.org/2000/svg"
                              fill="none"
                              viewBox="0 0 24 24"
                              strokeWidth={1.5}
                              stroke="currentColor"
                              className="w-5 h-5"
                            >
                              <path
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                d="M2.036 12.322a1.012 1.012 0 010-.639C3.423 7.51 7.36 4.5 12 4.5c4.638 0 8.573 3.007 9.963 7.178.07.207.07.431 0 .639C20.577 16.49 16.64 19.5 12 19.5c-4.638 0-8.573-3.007-9.963-7.178z"
                              />
                              <path
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
                              />
                            </svg>
                            Consult
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
        <TransactionModal
          isOpen={!!selectedTransaction}
          onClose={() => setSelectedTransaction(null)}
          transaction={selectedTransaction}
          product={
            selectedTransaction
              ? data.products.find((p) => p.sku === selectedTransaction.sku)
              : null
          }
        />
        <ProductModal
          isOpen={!!selectedProduct}
          onClose={() => setSelectedProduct(null)}
          product={selectedProduct}
          stockLevel={
            selectedProduct
              ? data.stock_levels.find((s) => s.sku === selectedProduct.sku)
              : null
          }
          onEdit={handleEditProduct}
        />
        <EditProductModal
          isOpen={!!editingProduct}
          onClose={() => setEditingProduct(null)}
          product={editingProduct}
          onSave={() => {
            setEditingProduct(null);
            fetchData();
          }}
        />
      </div>
    </div>
  );
};

export default Dashboard;
