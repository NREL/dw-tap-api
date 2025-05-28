import { useContext, useState } from "react";
import {
  Card,
  CardHeader,
  CardContent,
  CardActions,
  Button,
  Collapse,
  Typography,
  CircularProgress,
  Box,
} from "@mui/material";
import useSWR from "swr";
import { SettingsContext } from "../../providers/SettingsContext";
import ProductionTable from "./ProductionTable";
import { BaseTable } from "../../types/Tables";
import { getEnergyProduction } from "../../services/api";
import { productionConvert2Table } from "../../utils/production";

const defaultAverageProductionData = {
  "yearly_avg_energy_production": {'Lowest year': {'year': 2015, 'Average wind speed (m/s)': '3.88', 'kWh produced': 74708.0}, 'Average year': {'year': null, 'Average wind speed (m/s)': '4.19', 'kWh produced': 96544.0}, 'Highest year': {'year': 2014, 'Average wind speed (m/s)': '4.47', 'kWh produced': 118540.0}},
  "monthly_avg_energy_production": {'Jan': {'Average wind speed (m/s)': '4.49', 'kWh produced': 10196.0}, 'Feb': {'Average wind speed (m/s)': '4.44', 'kWh produced': 9410.0}, 'Mar': {'Average wind speed (m/s)': '4.52', 'kWh produced': 9751.0}, 'Apr': {'Average wind speed (m/s)': '4.55', 'kWh produced': 10009.0}, 'May': {'Average wind speed (m/s)': '4.31', 'kWh produced': 8618.0}, 'Jun': {'Average wind speed (m/s)': '4.14', 'kWh produced': 7800.0}, 'Jul': {'Average wind speed (m/s)': '3.86', 'kWh produced': 6272.0}, 'Aug': {'Average wind speed (m/s)': '3.81', 'kWh produced': 5936.0}, 'Sep': {'Average wind speed (m/s)': '3.71', 'kWh produced': 5305.0}, 'Oct': {'Average wind speed (m/s)': '3.86', 'kWh produced': 5971.0}, 'Nov': {'Average wind speed (m/s)': '4.19', 'kWh produced': 7821.0}, 'Dec': {'Average wind speed (m/s)': '4.45', 'kWh produced': 9455.0}}
}

const ResultCard = ({
  data,
}: {
  data: {
    title: string;
    subheader: string;
    data: string | number;
    details: string[];
  };

}) => {
  const [expanded, setExpanded] = useState(false);
  const { currentPosition, hubHeight, powerCurve, preferredModel } =
    useContext(SettingsContext);
  const { lat, lng } = currentPosition || {};
  const shouldFetch = data && data.title === "Production" && lat && lng && hubHeight && powerCurve && preferredModel;
  const { 
    isLoading: loadingProductionTable,
    data: averageProductionData,
    error: productionTableError,
  } = useSWR(
    expanded && shouldFetch ? { lat, lng, hubHeight, powerCurve, dataModel: preferredModel, time_period: "all" } : null,
    getEnergyProduction,
    { fallbackData: defaultAverageProductionData }
  );

  const productionTables: BaseTable[] = averageProductionData? 
    [
      productionConvert2Table(averageProductionData.yearly_avg_energy_production, 'Year'),
      productionConvert2Table(averageProductionData.monthly_avg_energy_production, 'Month')
    ] : 
    [
      productionConvert2Table(defaultAverageProductionData.yearly_avg_energy_production, 'Year'),
      productionConvert2Table(defaultAverageProductionData.monthly_avg_energy_production, 'Month')
    ];

  // console.log("Production tables", productionTables);

  const handleExpandClick = () => {
    setExpanded(!expanded);
  };

  return (
    <Card>
      <CardHeader
        title={data.title}
        subheader={data.subheader}
        sx={{ bgcolor: "var(--color-light)" }}
      />
      <CardContent>
        <Typography variant="body2" color="text.secondary">
          {data.data}
        </Typography>
      </CardContent>
      {data.details.length > 0 ? (
        <>
          <CardActions>
            <Button
              onClick={handleExpandClick}
              aria-expanded={expanded}
              aria-label="show more"
            >
              {expanded ? "Hide Details" : "Show Details"}
            </Button>
          </CardActions>
          <Collapse in={expanded} timeout="auto" unmountOnExit>
            <CardContent>
              {/* Text Details */}
              {data.details.map((detail, index) => (
                <Typography mb={2} key={data.title + "result_detail" + index} variant="body2">
                  {detail}
                </Typography>
              ))}
              {/* Table Details */}
              {data.title === "Production" && (loadingProductionTable ? (
                <CircularProgress size={24} />
              ) : productionTableError ? (
                <Typography color="error" variant="body2">
                  Error loading production table
                </Typography>
              ) : (
                <Box
                  sx = {{
                    display: "flex",
                    gap: 2,
                    flexWrap: "wrap",
                  }}
                >
                  {productionTables.map((table, index) => (
                    <Box
                      key={data.title + `table_${index}`}
                      sx={{ flex: 1, minWidth: "300px" }}>
                      <ProductionTable tableData={table} />
                    </Box>
                  ))}
                </Box>
              ))}
            </CardContent>
          </Collapse>
        </>
      ) : null}
    </Card>
  );
};

export default ResultCard;
