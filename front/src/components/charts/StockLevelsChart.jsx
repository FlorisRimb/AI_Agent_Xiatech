import * as Recharts from "recharts";

const StockLevelsChart = ({ stockLevels, products }) => {
  const chartData = stockLevels
    .map((stock) => {
      const product = products.find((p) => p.sku === stock.sku);
      const stockLevel = stock.stock_on_hand;
      let status;
      if (stockLevel < 50) {
        status = "Criticism";
      } else if (stockLevel < 100) {
        status = "Low";
      } else if (stockLevel < 200) {
        status = "Average";
      } else {
        status = "Bon";
      }

      return {
        name: product ? product.name : stock.sku,
        stock: stockLevel,
        category: product ? product.category : "N/A",
        status,
        fill:
          stockLevel < 50
            ? "var(--er)"
            : stockLevel < 100
            ? "var(--wa)"
            : stockLevel < 200
            ? "var(--in)"
            : "var(--su)",
      };
    })
    .sort((a, b) => a.stock - b.stock)
    .slice(0, 15);

  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="bg-base-100 p-4 rounded-lg shadow border border-base-300">
          <p className="font-bold">{data.name}</p>
          <p className="text-sm">Category: {data.category}</p>
          <p className="text-sm">Stock: {data.stock} units</p>
          <p className="text-sm">
            Status:{" "}
            <span
              className={
                data.status === "Criticism"
                  ? "text-error"
                  : data.status === "Low"
                  ? "text-warning"
                  : data.status === "Average"
                  ? "text-info"
                  : "text-success"
              }
            >
              {data.status}
            </span>
          </p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="w-full">
      <div className="flex gap-4 mb-4 justify-end">
        <div className="badge badge-error gap-2">Criticism (&lt;50)</div>
        <div className="badge badge-warning gap-2">Low (&lt;100)</div>
        <div className="badge badge-info gap-2">Average (&lt;200)</div>
        <div className="badge badge-success gap-2">Good (≥200)</div>
      </div>
      <Recharts.ResponsiveContainer width="100%" height={400}>
        <Recharts.BarChart
          data={chartData}
          layout="vertical"
          margin={{ top: 5, right: 30, left: 120, bottom: 5 }}
        >
          <Recharts.CartesianGrid strokeDasharray="3 3" horizontal={false} />
          <Recharts.XAxis type="number" domain={[0, "auto"]} />
          <Recharts.YAxis
            type="category"
            dataKey="name"
            width={100}
            tick={{ fill: "var(--bc)" }}
          />
          <Recharts.Tooltip content={<CustomTooltip />} />
          <Recharts.Legend />
          <Recharts.Bar
            dataKey="stock"
            name="Stock level"
            fill="var(--p)"
            radius={[0, 4, 4, 0]}
          >
            {chartData.map((entry, index) => (
              <Recharts.Cell key={`cell-${index}`} fill={entry.fill} />
            ))}
          </Recharts.Bar>
        </Recharts.BarChart>
      </Recharts.ResponsiveContainer>
    </div>
  );
};

export default StockLevelsChart;
