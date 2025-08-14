// UploadExcelField.jsx
import React from "react";
import { useFormContext } from "react-hook-form";
import { FormField, FormItem, FormLabel, FormControl, FormDescription, FormMessage } from "./form"; // ajuste o caminho conforme sua estrutura

export function UploadExcelField({
  name = "excelFile",
  label = "Planilha Excel",
  description = "Envie um arquivo .xlsx ou .xls com as experiências.",
  accept = ".xlsx,.xls",
}) {
  const { control } = useFormContext();

  return (
    <FormField
      control={control}
      name={name}
      render={({ field }) => (
        <FormItem>
          <FormLabel>{label}</FormLabel>
          <FormControl>
            {/* FormControl usa Radix Slot, então o input deve ser filho */}
            <input
              type="file"
              accept={accept}
              name={field.name}
              ref={field.ref}
              onBlur={field.onBlur}
              onChange={(e) => {
                const file = e.target.files?.[0] ?? null;
                field.onChange(file);
              }}
            />
          </FormControl>
          <FormDescription>{description}</FormDescription>
          <FormMessage />
        </FormItem>
      )}
    />
  );
}