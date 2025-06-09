import { useContext, useState } from "react";
import {
  Card,
  CardHeader,
  CardContent,
  CardActions,
  Button,
  Collapse,
  Typography,
  Box,
  Divider,
  Chip,
  Paper,
  Skeleton,
} from "@mui/material";
import useSWR from "swr";
import { SettingsContext } from "../../providers/SettingsContext";
import { UnitsContext } from "../../providers/UnitsContext";
import ProductionDataTable from "./ProductionDataTable";
import { getEnergyProduction } from "../../services/api";
import { convertOutput } from "../../utils";
import { ExpandMore, ExpandLess } from "@mui/icons-material";

const ProductionCard = () => {
  const [expanded, setExpanded] = useState(false);
  const { currentPosition, hubHeight, powerCurve, preferredModel: dataModel } = useContext(SettingsContext);
  const { units } = useContext(UnitsContext);
  const { lat, lng } = currentPosition || {};
  
  const title = "Production";
  const subheader = "Estimated annual production potential";
  const details = [
    "The wind resource, and by extension the energy production, varies month to month and year to year. It is important to understand the average characteristics as well as the variability you can expect to see from your wind turbine on any given year."
  ];
  
  const shouldFetch = lat && lng && hubHeight && powerCurve && dataModel;
  const { 
    isLoading,
    data: productionData,
    error,
  } = useSWR(
    shouldFetch ? { lat, lng, hubHeight, powerCurve, dataModel, time_period: "all" } : null,
    getEnergyProduction
  );

  const handleExpandClick = () => {
    setExpanded(!expanded);
  };

  // Loading state
  if (isLoading) {
    return (
      <Card>
        <CardHeader
          title={
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              {title}
              <Chip 
                label="Primary Analysis" 
                size="small" 
                color="primary" 
                variant="outlined"
              />
            </Box>
          }
          subheader={subheader}
          sx={{ bgcolor: "var(--color-light)", pb: 1 }}
        />
        
        <CardContent sx={{ pb: 2 }}>
          {/* Skeleton for production metrics */}
          <Box sx={{ 
            display: 'grid', 
            gridTemplateColumns: { 
              xs: '1fr', 
              sm: '1fr', 
              md: 'repeat(3, 1fr)' 
            }, 
            gap: 2, 
            mb: 3 
          }}>
            {[1, 2, 3].map((index) => (
              <Paper key={index} sx={{ p: 2, textAlign: 'center' }}>
                <Skeleton variant="text" width="60%" height={20} sx={{ mx: 'auto' }} />
                <Skeleton variant="text" width="80%" height={40} sx={{ mx: 'auto', mt: 0.5 }} />
                <Skeleton variant="text" width="40%" height={16} sx={{ mx: 'auto' }} />
              </Paper>
            ))}
          </Box>

          {/* Skeleton for details */}
          <Skeleton variant="text" width="100%" height={20} />
          <Skeleton variant="text" width="90%" height={20} />
        </CardContent>

        <Divider sx={{ borderStyle: 'dotted' }} />

        <CardActions sx={{ justifyContent: 'space-between', px: 2}}>
          <Skeleton variant="text" width="150px" height={20} />
          <Skeleton variant="rectangular" width="60px" height={32} />
        </CardActions>
      </Card>
    );
  }

  // Error state
  if (error) {
    return (
      <Card>
        <CardHeader
          title={
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              {title}
              <Chip 
                label="Primary Analysis" 
                size="small" 
                color="error" 
                variant="outlined"
              />
            </Box>
          }
          subheader={subheader}
          sx={{ bgcolor: "var(--color-light)", pb: 1 }}
        />
        
        <CardContent sx={{ py: 4, textAlign: 'center' }}>
          <Typography color="error" variant="h6" gutterBottom>
            Error Loading Production Data
          </Typography>
          <Typography color="text.secondary" variant="body2">
            Unable to load production analysis. Please check your settings and try again.
          </Typography>
        </CardContent>
      </Card>
    );
  }

  // No data state
  if (!productionData) {
    return (
      <Card>
        <CardHeader
          title={
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              {title}
              <Chip 
                label="Primary Analysis" 
                size="small" 
                color="default" 
                variant="outlined"
              />
            </Box>
          }
          subheader={subheader}
          sx={{ bgcolor: "var(--color-light)", pb: 1 }}
        />
        
        <CardContent sx={{ py: 4, textAlign: 'center' }}>
          <Typography color="text.secondary" variant="h6" gutterBottom>
            No Production Data Available
          </Typography>
          <Typography color="text.secondary" variant="body2">
            Please set your location and turbine settings to see production analysis.
          </Typography>
        </CardContent>
      </Card>
    );
  }

  // Data loaded successfully
  const yearlyData = productionData.yearly_avg_energy_production;
  const avgProduction = yearlyData?.['Average year']?.['kWh produced'] || 0;
  const lowProduction = yearlyData?.['Lowest year']?.['kWh produced'] || 0;
  const highProduction = yearlyData?.['Highest year']?.['kWh produced'] || 0;

  return (
    <Card>
      <CardHeader
        title={
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            {title}
            <Chip 
              label="Primary Analysis" 
              size="small" 
              color="primary" 
              variant="outlined"
            />
          </Box>
        }
        subheader={subheader}
        sx={{ bgcolor: "var(--color-light)", pb: 1 }}
      />
      
      {/* Key Production Metrics - Always Visible */}
      <CardContent sx={{ pb: 2 }}>
        <Box sx={{ 
          display: 'grid', 
          gridTemplateColumns: { 
            xs: '1fr', 
            sm: '1fr', 
            md: 'repeat(3, 1fr)' 
          }, 
          gap: 2, 
          mb: 3 
        }}>
          <Paper sx={{ p: 2, textAlign: 'center', bgcolor: 'primary.light', color: 'primary.contrastText' }}>
            <Typography variant="caption" sx={{ opacity: 0.9 }}>
              Average 
            </Typography>
            <Typography variant="h5" sx={{ fontWeight: 'bold', mt: 0.5 }}>
              {convertOutput(Number(avgProduction), units.output).replace(/\s\w+$/, '')}
            </Typography>
            <Typography variant="caption">{units.output}</Typography>
          </Paper>
          
          <Paper sx={{ p: 2, textAlign: 'center', bgcolor: 'success.light', color: 'success.contrastText' }}>
            <Typography variant="caption" sx={{ opacity: 0.9 }}>
              Highest Year
            </Typography>
            <Typography variant="h6" sx={{ fontWeight: 'bold', mt: 0.5 }}>
              {convertOutput(Number(highProduction), units.output).replace(/\s\w+$/, '')}
            </Typography>
            <Typography variant="caption">{units.output}</Typography>
          </Paper>
          
          <Paper sx={{ p: 2, textAlign: 'center', bgcolor: 'warning.light', color: 'warning.contrastText' }}>
            <Typography variant="caption" sx={{ opacity: 0.9 }}>
              Lowest Year
            </Typography>
            <Typography variant="h6" sx={{ fontWeight: 'bold', mt: 0.5 }}>
              {convertOutput(Number(lowProduction), units.output).replace(/\s\w+$/, '')}
            </Typography>
            <Typography variant="caption">{units.output}</Typography>
          </Paper>
        </Box>

        {details.map((detail, index) => (
          <Typography mb={1} key={title + "result_detail" + index} variant="body2" color="text.secondary">
            {detail}
          </Typography>
        ))}
      </CardContent>

      <Divider sx={{ borderStyle: 'dotted' }} />

      {/* Detailed Breakdown - Expandable */}
      <CardActions sx={{ justifyContent: 'space-between', px: 2}}>
        <Typography variant="body2" color="text.secondary" sx={{ 
          display: { xs: 'none', sm: 'block' } // Hide on mobile to save space
        }}>
          Monthly Production Details
        </Typography>
        <Button
          onClick={handleExpandClick}
          aria-expanded={expanded}
          aria-label="show detailed breakdown"
          variant="outlined"
          size="small"
          startIcon={expanded ? <ExpandLess /> : <ExpandMore />}
          sx={{
            whiteSpace: 'nowrap',
            minWidth: 'auto',
            fontSize: { xs: '0.75rem', sm: '0.875rem' },
            px: { xs: 1, sm: 2 }
          }}
        >
          {expanded ? "Hide" : "Show"}
        </Button>
      </CardActions>

      <Collapse in={expanded} timeout="auto" unmountOnExit>
        <CardContent sx={{ pt: 0 }}>
          <ProductionDataTable 
            title=""
            data={productionData.monthly_avg_energy_production}
          />
        </CardContent>
      </Collapse>
    </Card>
  );
};

export default ProductionCard; 