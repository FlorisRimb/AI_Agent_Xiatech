const TransactionModal = ({ isOpen, onClose, transaction, product }) => {
  if (!isOpen || !transaction) return null;

  return (
    <div className="modal modal-open">
      <div className="modal-box">
        <h3 className="font-bold text-lg">
          Transaction details {transaction.transaction_id}
        </h3>

        <div className="py-4 space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <p className="text-sm font-semibold text-base-content/70">Date</p>
              <p className="font-medium">
                {new Date(transaction.timestamp).toLocaleString()}
              </p>
            </div>
            <div className="space-y-2">
              <p className="text-sm font-semibold text-base-content/70">
                Quantité
              </p>
              <p className="font-medium">{transaction.quantity} unity</p>
            </div>
          </div>

          {product && (
            <div className="space-y-4 mt-4">
              <h4 className="font-semibold">Product details</h4>
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <p className="text-sm font-semibold text-base-content/70">
                    Name
                  </p>
                  <p className="font-medium">{product.name}</p>
                </div>
                <div className="space-y-2">
                  <p className="text-sm font-semibold text-base-content/70">
                    SKU
                  </p>
                  <p className="font-medium">{product.sku}</p>
                </div>
                <div className="space-y-2">
                  <p className="text-sm font-semibold text-base-content/70">
                    Category
                  </p>
                  <div className="badge badge-ghost">{product.category}</div>
                </div>
                <div className="space-y-2">
                  <p className="text-sm font-semibold text-base-content/70">
                    Price for unit
                  </p>
                  <p className="font-medium">{product.price.toFixed(2)}€</p>
                </div>
              </div>

              <div className="mt-4 p-4 bg-base-200 rounded-lg">
                <div className="flex justify-between items-center">
                  <span className="text-sm font-semibold">Total amount</span>
                  <span className="text-lg font-bold">
                    {(product.price * transaction.quantity).toFixed(2)}€
                  </span>
                </div>
              </div>
            </div>
          )}
        </div>

        <div className="modal-action">
          <button className="btn" onClick={onClose}>
            Close
          </button>
        </div>
      </div>
      <div className="modal-backdrop" onClick={onClose}>
        <button className="cursor-default">Close</button>
      </div>
    </div>
  );
};

export default TransactionModal;
