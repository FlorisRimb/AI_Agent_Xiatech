import * as Recharts from "recharts";

const SalesChart = ({ data }) => {
  // Préparer les données pour le graphique
  const chartData = Object.entries(data).map(([category, sales]) => ({
    category,
    ventes: sales,
  }));

  return (
    <Recharts.ResponsiveContainer width="100%" height={300}>
      <Recharts.BarChart data={chartData}>
        <Recharts.CartesianGrid strokeDasharray="3 3" />
        <Recharts.XAxis dataKey="category" />
        <Recharts.YAxis />
        <Recharts.Tooltip
          contentStyle={{
            backgroundColor: "var(--b1)",
            border: "1px solid var(--b3)",
          }}
          labelStyle={{ color: "var(--bc)" }}
        />
        <Recharts.Legend />
        <Recharts.Bar dataKey="ventes" fill="var(--p)" name="Sales" />
      </Recharts.BarChart>
    </Recharts.ResponsiveContainer>
  );
};

export default SalesChart;
