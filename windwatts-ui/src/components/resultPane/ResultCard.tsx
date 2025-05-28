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
import { getProductionTables } from "../../services/api";
import { SettingsContext } from "../../providers/SettingsContext";
import ProductionTable from "./ProductionTable";
import { productionConvert2Table } from "../../utils/production";
import { BaseTable } from "../../types/Tables";

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
  const { currentPosition, hubHeight, powerCurve } =
    useContext(SettingsContext);
  const { lat, lng } = currentPosition || {};
  const shouldFetch = data && data.title === "Production" && lat && lng && hubHeight;
  const { 
    isLoading: loadingProductionTable,
    data: averageProductionData,
    error: productionTableError,
  } = useSWR(
    expanded && shouldFetch ? { lat, lng, hubHeight, powerCurve } : null,
    getProductionTables
  );

  const defaultAverageProductionData = {
    'yearly': {'L': {'year': 11, 'Average wind speed (m/s)': '3.88', 'kWh produced': 74708.0}, 'A': {'year': null, 'Average wind speed (m/s)': '4.19', 'kWh produced': 96544.0}, 'H': {'year': 2014, 'Average wind speed (m/s)': '4.47', 'kWh produced': 118540.0}},
    'monthly': {'Jan': {'Average wind speed (m/s)': '4.49', 'kWh produced': 10196.0}}
  }

  console.log("Average production data", averageProductionData);
  const productionTables: BaseTable[] = averageProductionData? 
    [
      productionConvert2Table(averageProductionData.yearly, 'Year'),
      productionConvert2Table(averageProductionData.monthly, 'Month')
    ] : 
    [
      productionConvert2Table(defaultAverageProductionData.yearly, 'Year'),
      productionConvert2Table(defaultAverageProductionData.monthly, 'Month')
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
                <Typography key={data.title + "result_detail" + index} variant="body2">
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
