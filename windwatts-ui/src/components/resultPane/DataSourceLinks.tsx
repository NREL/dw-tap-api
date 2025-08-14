import { Link, Typography } from "@mui/material";
import { DATA_MODEL_INFO } from "../../constants";
import { DataModel } from "../../types";

export const DataSourceLinks = ({
  preferredModel,
}: {
  preferredModel: DataModel;
}) => {
  return (
    <Typography variant="body2" color="text.secondary">
      * Estimates based on{" "}
      <Link
        href={
          DATA_MODEL_INFO[preferredModel]?.source_href ||
          DATA_MODEL_INFO.era5.source_href
        }
        target="_blank"
        rel="noopener noreferrer"
        underline="hover"
      >
        {DATA_MODEL_INFO[preferredModel]?.label || DATA_MODEL_INFO.era5.label}{" "}
        data
      </Link>
      {DATA_MODEL_INFO[preferredModel]?.help_href && (
        <>
          {" - "}
          <Link
            href={DATA_MODEL_INFO[preferredModel]!.help_href}
            target="_blank"
            rel="noopener noreferrer"
            underline="hover"
          >
            learn more
          </Link>
        </>
      )}
      .
    </Typography>
  );
};
