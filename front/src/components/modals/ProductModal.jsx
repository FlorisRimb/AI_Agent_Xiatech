const ProductModal = ({ isOpen, onClose, product, stockLevel, onEdit }) => {
  if (!isOpen || !product) return null;

  return (
    <div className="modal modal-open">
      <div className="modal-box">
        <h3 className="font-bold text-lg mb-4">
          Product details {product.name}
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="space-y-4">
            <div>
              <h4 className="font-semibold mb-2">General information</h4>
              <div className="bg-base-200 p-4 rounded-lg space-y-3">
                <div>
                  <p className="text-sm text-base-content/70">SKU</p>
                  <p className="font-medium">{product.sku}</p>
                </div>
                <div>
                  <p className="text-sm text-base-content/70">Category</p>
                  <div className="badge badge-ghost mt-1">
                    {product.category}
                  </div>
                </div>
                <div>
                  <p className="text-sm text-base-content/70">Price</p>
                  <p className="font-medium text-lg">
                    {product.price.toFixed(2)}€
                  </p>
                </div>
              </div>
            </div>
          </div>

          <div className="space-y-4">
            <div>
              <h4 className="font-semibold mb-2">Stock status</h4>
              <div className="bg-base-200 p-4 rounded-lg space-y-3">
                <div>
                  <p className="text-sm text-base-content/70">Current stock</p>
                  <div
                    className={`badge ${
                      stockLevel?.stock_on_hand < 50
                        ? "badge-error"
                        : "badge-success"
                    } badge-lg mt-1`}
                  >
                    {stockLevel?.stock_on_hand || 0} units
                  </div>
                </div>
                <div>
                  <p className="text-sm text-base-content/70">Status</p>
                  <p
                    className={`font-medium ${
                      stockLevel?.stock_on_hand < 50
                        ? "text-error"
                        : "text-success"
                    }`}
                  >
                    {stockLevel?.stock_on_hand < 50
                      ? "Stock faible"
                      : "Stock suffisant"}
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="modal-action">
          <button className="btn btn-ghost" onClick={onClose}>
            Fermer
          </button>
          <button
            className="btn btn-primary"
            onClick={() => {
              onEdit(product);
              onClose();
            }}
          >
            Edit product
          </button>
        </div>
      </div>
      <div className="modal-backdrop" onClick={onClose}>
        <button className="cursor-default">Close</button>
      </div>
    </div>
  );
};

export default ProductModal;
