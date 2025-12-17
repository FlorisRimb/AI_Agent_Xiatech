import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";

const SalesTimelineChart = ({ sales }) => {
  // Grouper les ventes par date
  const salesByDate = sales.reduce((acc, sale) => {
    const date = new Date(sale.timestamp).toLocaleDateString();
    acc[date] = (acc[date] || 0) + sale.quantity;
    return acc;
  }, {});

  const chartData = Object.entries(salesByDate).map(([date, quantity]) => ({
    date,
    quantité: quantity,
  }));

  return (
    <ResponsiveContainer width="100%" height={300}>
      <LineChart data={chartData}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="date" />
        <YAxis />
        <Tooltip
          contentStyle={{
            backgroundColor: "var(--b1)",
            border: "1px solid var(--b3)",
          }}
          labelStyle={{ color: "var(--bc)" }}
        />
        <Legend />
        <Line
          type="monotone"
          dataKey="quantité"
          stroke="var(--s)"
          name="Quantity sold"
          strokeWidth={2}
        />
      </LineChart>
    </ResponsiveContainer>
  );
};

export default SalesTimelineChart;
