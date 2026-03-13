#!/usr/bin/env python3
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sheets_client import SheetsClient

def analyze_spreadsheet():
    client = SheetsClient()
    sheet_id = "1QuYN01Rhgua_Em8SE5CIXOzFa8kULWnxFE2_ZOc_P74"
    
    try:
        # Get spreadsheet metadata
        spreadsheet = client.service.spreadsheets().get(spreadsheetId=sheet_id).execute()
        
        print(f"Spreadsheet Title: {spreadsheet.get('properties', {}).get('title', 'Unknown')}")
        print(f"Total Sheets/Tabs: {len(spreadsheet.get('sheets', []))}")
        print("\n" + "="*60)
        
        for i, sheet in enumerate(spreadsheet.get('sheets', []), 1):
            sheet_props = sheet.get('properties', {})
            sheet_name = sheet_props.get('title', f'Sheet{i}')
            grid_props = sheet_props.get('gridProperties', {})
            
            print(f"\nTab {i}: {sheet_name}")
            print(f"  Rows: {grid_props.get('rowCount', 'Unknown')}")
            print(f"  Columns: {grid_props.get('columnCount', 'Unknown')}")
            
            # Get actual data to analyze content
            try:
                range_name = f"{sheet_name}!A1:Z1000"
                result = client.service.spreadsheets().values().get(
                    spreadsheetId=sheet_id, range=range_name
                ).execute()
                
                values = result.get('values', [])
                if values:
                    actual_rows = len(values)
                    actual_cols = max(len(row) for row in values) if values else 0
                    
                    print(f"  Actual Data Rows: {actual_rows}")
                    print(f"  Actual Data Columns: {actual_cols}")
                    
                    if len(values) > 0:
                        print(f"  Headers: {values[0][:10]}{'...' if len(values[0]) > 10 else ''}")
                    
                    # Sample data types
                    if len(values) > 1:
                        sample_row = values[1]
                        print(f"  Sample Data: {sample_row[:5]}{'...' if len(sample_row) > 5 else ''}")
                        
                        # Analyze data types
                        data_types = []
                        for j, cell in enumerate(sample_row[:10]):
                            if cell.isdigit():
                                data_types.append(f"Col{j+1}:int")
                            elif cell.replace('.', '').isdigit():
                                data_types.append(f"Col{j+1}:float")
                            elif '-' in cell and len(cell) == 10:
                                data_types.append(f"Col{j+1}:date")
                            else:
                                data_types.append(f"Col{j+1}:str")
                        
                        print(f"  Data Types: {', '.join(data_types)}")
                else:
                    print("  No data found")
                    
            except Exception as e:
                print(f"  Error reading data: {str(e)}")
        
        print("\n" + "="*60)
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    analyze_spreadsheet()