const StockComparison = ({ stocks }) => {
  if (!stocks || stocks.length === 0) {
    return null;
  }

  // Filtrer les produits avec commandes en attente ou stock faible
  const relevantStocks = stocks.filter(
    (stock) => stock.pending_orders_quantity > 0 || stock.stock_on_hand < 100
  );

  if (relevantStocks.length === 0) {
    return null;
  }

  return (
    <div className="card bg-base-100 shadow-xl">
      <div className="card-body">
        <h3 className="card-title text-primary">
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
              d="M3.75 3v11.25A2.25 2.25 0 006 16.5h2.25M3.75 3h-1.5m1.5 0h16.5m0 0h1.5m-1.5 0v11.25A2.25 2.25 0 0118 16.5h-2.25m-7.5 0h7.5m-7.5 0l-1 3m8.5-3l1 3m0 0l.5 1.5m-.5-1.5h-9.5m0 0l-.5 1.5M9 11.25v1.5M12 9v3.75m3-6v6"
            />
          </svg>
          Stock Réel vs Stock Virtuel
        </h3>
        <div className="divider mt-0"></div>
        
        <div className="overflow-x-auto">
          <table className="table table-zebra">
            <thead>
              <tr>
                <th>Produit</th>
                <th>Stock Réel</th>
                <th>En Transit</th>
                <th>Stock Virtuel</th>
                <th>Évolution</th>
              </tr>
            </thead>
            <tbody>
              {relevantStocks.map((stock) => {
                const percentageIncrease = stock.stock_on_hand > 0
                  ? ((stock.virtual_stock - stock.stock_on_hand) / stock.stock_on_hand * 100).toFixed(0)
                  : 0;
                
                const isLowStock = stock.stock_on_hand < 50;
                const hasPendingOrders = stock.pending_orders_quantity > 0;

                return (
                  <tr key={stock.sku} className="hover">
                    <td>
                      <div>
                        <div className="font-medium">{stock.product_name}</div>
                        <div className="badge badge-sm badge-outline">
                          {stock.sku}
                        </div>
                      </div>
                    </td>
                    <td>
                      <div className={`badge gap-2 ${isLowStock ? 'badge-error' : 'badge-ghost'}`}>
                        <svg
                          xmlns="http://www.w3.org/2000/svg"
                          fill="none"
                          viewBox="0 0 24 24"
                          className="inline-block w-4 h-4 stroke-current"
                        >
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth="2"
                            d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"
                          />
                        </svg>
                        {stock.stock_on_hand} unités
                      </div>
                    </td>
                    <td>
                      {hasPendingOrders ? (
                        <div className="badge badge-warning gap-2">
                          <span className="loading loading-spinner loading-xs"></span>
                          +{stock.pending_orders_quantity} en transit
                        </div>
                      ) : (
                        <div className="badge badge-ghost">Aucune</div>
                      )}
                    </td>
                    <td>
                      <div className="badge badge-success gap-2">
                        <svg
                          xmlns="http://www.w3.org/2000/svg"
                          fill="none"
                          viewBox="0 0 24 24"
                          className="inline-block w-4 h-4 stroke-current"
                        >
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth="2"
                            d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                          />
                        </svg>
                        {stock.virtual_stock} unités
                      </div>
                    </td>
                    <td>
                      {hasPendingOrders ? (
                        <div className="flex items-center gap-2">
                          <progress
                            className="progress progress-success w-20"
                            value={percentageIncrease}
                            max="100"
                          ></progress>
                          <span className="text-success font-semibold">
                            +{percentageIncrease}%
                          </span>
                        </div>
                      ) : (
                        <span className="text-base-content/50">-</span>
                      )}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>

        {relevantStocks.some((s) => s.pending_orders_quantity > 0) && (
          <div className="alert alert-info mt-4">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              className="stroke-current shrink-0 w-6 h-6"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth="2"
                d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
            <div>
              <h3 className="font-bold">Commandes en transit</h3>
              <div className="text-xs">
                Les commandes seront automatiquement reçues dans 30 secondes. Le stock réel sera alors mis à jour.
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default StockComparison;
