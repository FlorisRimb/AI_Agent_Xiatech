const AIAnalysis = ({ analysis, onReceiveOrders, isReceiving }) => {
  if (!analysis) {
    return null;
  }

  const { low_stock_products, orders_placed, summary } = analysis;
  
  // Compter les commandes en attente (non reçues)
  const hasPendingOrders = summary.total_orders > 0;

  return (
    <div className="space-y-4">
      {/* Résumé */}
      <div className="stats stats-vertical lg:stats-horizontal shadow w-full">
        <div className="stat">
          <div className="stat-figure text-warning">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              className="inline-block w-8 h-8 stroke-current"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth="2"
                d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
              />
            </svg>
          </div>
          <div className="stat-title">Produits en Alerte</div>
          <div className="stat-value text-warning">
            {summary.total_low_stock}
          </div>
          <div className="stat-desc">Risque de rupture de stock</div>
        </div>

        <div className="stat">
          <div className="stat-figure text-success">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              className="inline-block w-8 h-8 stroke-current"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth="2"
                d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
          </div>
          <div className="stat-title">Commandes Passées</div>
          <div className="stat-value text-success">{summary.total_orders}</div>
          <div className="stat-desc">Par l'IA automatiquement</div>
        </div>

        <div className="stat">
          <div className="stat-figure text-primary">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              className="inline-block w-8 h-8 stroke-current"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth="2"
                d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"
              />
            </svg>
          </div>
          <div className="stat-title">Unités Commandées</div>
          <div className="stat-value text-primary">
            {summary.total_units_ordered}
          </div>
          <div className="stat-desc">Total réapprovisionné</div>
        </div>
      </div>

      {/* Bouton pour recevoir les commandes */}
      {hasPendingOrders && (
        <div className="alert alert-info">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" className="stroke-current shrink-0 w-6 h-6">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <div className="flex-1">
            <h3 className="font-bold">Commandes en attente de réception</h3>
            <div className="text-xs">Les produits sont commandés mais le stock n'est pas encore mis à jour. Cliquez pour simuler la réception de la marchandise.</div>
          </div>
          <button 
            className={`btn btn-success ${isReceiving ? 'loading' : ''}`}
            onClick={onReceiveOrders}
            disabled={isReceiving}
          >
            {isReceiving ? (
              <>
                <span className="loading loading-spinner"></span>
                Réception en cours...
              </>
            ) : (
              <>
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-5 h-5">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                Recevoir les Commandes
              </>
            )}
          </button>
        </div>
      )}

      {/* Produits en Rupture de Stock */}
      {low_stock_products.length > 0 && (
        <div className="card bg-base-100 shadow-xl">
          <div className="card-body">
            <h3 className="card-title text-warning">
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
                  d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z"
                />
              </svg>
              Produits en Rupture de Stock Détectés
            </h3>
            <div className="divider mt-0"></div>
            <div className="overflow-x-auto">
              <table className="table table-zebra">
                <thead>
                  <tr>
                    <th>SKU</th>
                    <th>Nom du Produit</th>
                    <th>Catégorie</th>
                    <th>Stock Actuel</th>
                    <th>Prix Unitaire</th>
                  </tr>
                </thead>
                <tbody>
                  {low_stock_products.map((product) => (
                    <tr key={product.sku} className="hover">
                      <td>
                        <div className="badge badge-outline">{product.sku}</div>
                      </td>
                      <td className="font-medium">{product.name}</td>
                      <td>
                        <div className="badge badge-ghost">
                          {product.category}
                        </div>
                      </td>
                      <td>
                        <div className="badge badge-warning gap-2">
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
                              d="M6 18L18 6M6 6l12 12"
                            />
                          </svg>
                          {product.current_stock} unités
                        </div>
                      </td>
                      <td className="font-mono">
                        {product.price.toFixed(2)} €
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* Commandes Passées */}
      {orders_placed.length > 0 && (
        <div className="card bg-base-100 shadow-xl">
          <div className="card-body">
            <h3 className="card-title text-success">
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
                  d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
              Commandes de Réapprovisionnement Automatiques
            </h3>
            <div className="divider mt-0"></div>
            <div className="overflow-x-auto">
              <table className="table table-zebra">
                <thead>
                  <tr>
                    <th>ID Commande</th>
                    <th>Produit</th>
                    <th>Quantité</th>
                    <th>Coût Estimé</th>
                    <th>Date</th>
                  </tr>
                </thead>
                <tbody>
                  {orders_placed.map((order) => (
                    <tr key={order.order_id} className="hover">
                      <td>
                        <div className="font-mono text-xs">
                          {order.order_id}
                        </div>
                      </td>
                      <td>
                        <div>
                          <div className="font-medium">
                            {order.product_name}
                          </div>
                          <div className="badge badge-sm badge-outline">
                            {order.sku}
                          </div>
                        </div>
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
                              d="M4.5 10.5L12 3m0 0l7.5 7.5M12 3v18"
                            />
                          </svg>
                          {order.quantity} unités
                        </div>
                      </td>
                      <td className="font-mono text-success">
                        {order.estimated_cost.toFixed(2)} €
                      </td>
                      <td className="text-sm opacity-70">
                        {new Date(order.order_date).toLocaleString("fr-FR")}
                      </td>
                    </tr>
                  ))}
                </tbody>
                <tfoot>
                  <tr>
                    <th colSpan="3" className="text-right">
                      Total :
                    </th>
                    <th className="font-mono text-lg text-success">
                      {orders_placed
                        .reduce((sum, o) => sum + o.estimated_cost, 0)
                        .toFixed(2)}{" "}
                      €
                    </th>
                    <th></th>
                  </tr>
                </tfoot>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* Message si pas de résultats */}
      {low_stock_products.length === 0 && orders_placed.length === 0 && (
        <div className="alert alert-info">
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
          <span>Aucune action requise. Tous les stocks sont à niveau.</span>
        </div>
      )}
    </div>
  );
};

export default AIAnalysis;
