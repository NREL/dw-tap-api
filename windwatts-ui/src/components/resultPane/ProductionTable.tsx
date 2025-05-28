import { Table, TableBody, TableCell, TableHead, TableRow, Typography } from "@mui/material";
import type { BaseTable } from "../../types/Tables";

const ProductionTable = (
  { tableData }: { tableData: BaseTable }
 ) => {
  return (
    <>
    <Typography variant="h6" gutterBottom>
        {tableData.title}
      </Typography>
      <Table
        size="small"
        aria-label={ tableData.title }
        sx={{ border: 1, borderColor: "divider" }}>
        <TableHead>
          <TableRow>
            {tableData.headers.map((header, index) => (
              <TableCell key={`header_${index}`}>{header}</TableCell>
            ))}
          </TableRow>
        </TableHead>
        <TableBody>
          {tableData.rows.map((row, rowIndex) => (
            <TableRow key={`row_${rowIndex}`}>
              {row.map((cell, cellIndex) => (
                <TableCell key={`cell_${rowIndex}_${cellIndex}`}>{cell}</TableCell>
              ))}
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </>
  );
}

export default ProductionTable;