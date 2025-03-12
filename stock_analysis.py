import pandas as pd
import sys
import matplotlib.pyplot as plt
from PyQt6 import uic
from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QTableWidgetItem, QMessageBox
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas


class StockAnalysisApp(QMainWindow):
    def __init__(self):
        super().__init__()

        # Load the UI file
        uic.loadUi('stock_analysis.ui', self)

        # Load data
        self.load_data()

        # Set up matplotlib figure and canvas
        self.figure = plt.figure(figsize=(12, 4))
        self.canvas = FigureCanvas(self.figure)
        chart_layout = QVBoxLayout(self.chartWidget)
        chart_layout.addWidget(self.canvas)

        # Connect buttons to functions
        self.searchButton.clicked.connect(self.search_and_modify)
        self.addButton.clicked.connect(self.add_data)
        self.deleteButton.clicked.connect(self.delete_data)
        self.sortButton.clicked.connect(self.sort_by_price)
        self.statsButton.clicked.connect(self.calculate_stats)
        self.chartButton.clicked.connect(self.generate_charts)

        # Update table with initial data
        self.update_table()

        # Generate initial charts
        self.generate_charts()

    def load_data(self):
        try:
            # For this example, we'll use a local file path
            # In a real application, you would use the URL: https://tranduythanh.com/datasets/SampleData2.csv
            # self.df = pd.read_csv("https://tranduythanh.com/datasets/SampleData2.csv")

            # For demonstration, I'll create sample data similar to what might be in the file
            data = {
                'Symbol': ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'TSLA', 'NVDA', 'JPM'],
                'Price': [180.5, 350.2, 140.8, 130.5, 300.7, 250.3, 450.2, 140.6],
                'PE': [28.5, 32.1, 25.7, 40.2, 22.3, 60.5, 45.8, 12.3],
                'Group': ['Tech', 'Tech', 'Tech', 'Retail', 'Tech', 'Auto', 'Tech', 'Finance']
            }
            self.df = pd.DataFrame(data)

            # Add USD column (requirement 4)
            self.df['USD'] = self.df['Price'] / 23

            print("Data loaded successfully:")
            print(self.df)  # Requirement 1: Print all data
        except Exception as e:
            print(f"Error loading data: {e}")
            # Create empty DataFrame with the same structure if loading fails
            self.df = pd.DataFrame(columns=['Symbol', 'Price', 'PE', 'Group', 'USD'])

    def update_table(self):
        # Update the table with current DataFrame data
        self.tableWidget.setRowCount(len(self.df))
        self.tableWidget.setColumnCount(len(self.df.columns))
        self.tableWidget.setHorizontalHeaderLabels(self.df.columns)

        # Fill the table with data
        for row in range(len(self.df)):
            for col in range(len(self.df.columns)):
                value = str(self.df.iloc[row, col])
                item = QTableWidgetItem(value)
                self.tableWidget.setItem(row, col, item)

        # Resize columns to content
        self.tableWidget.resizeColumnsToContents()

    def search_and_modify(self):
        # Requirement 3: Search by Symbol and reduce Price by 1/2
        symbol = self.symbolInput.text().strip()
        if not symbol:
            QMessageBox.warning(self, "Input Error", "Please enter a symbol to search.")
            return

        if symbol in self.df['Symbol'].values:
            self.df.loc[self.df['Symbol'] == symbol, 'Price'] /= 2
            # Update USD column after price change
            self.df['USD'] = self.df['Price'] / 23
            self.update_table()
            QMessageBox.information(self, "Success", f"Price for {symbol} reduced by half.")
        else:
            QMessageBox.warning(self, "Not Found", f"Symbol {symbol} not found in the data.")

    def add_data(self):
        # Requirement 5: Add new data to DataFrame
        try:
            symbol = self.newSymbol.text().strip()
            price = float(self.newPrice.text().strip())
            pe = float(self.newPE.text().strip())
            group = self.newGroup.text().strip()

            if not all([symbol, self.newPrice.text(), self.newPE.text(), group]):
                QMessageBox.warning(self, "Input Error", "All fields are required.")
                return

            # Calculate USD
            usd = price / 23

            # Add new row to DataFrame
            new_row = pd.DataFrame({
                'Symbol': [symbol],
                'Price': [price],
                'PE': [pe],
                'Group': [group],
                'USD': [usd]
            })

            self.df = pd.concat([self.df, new_row], ignore_index=True)
            self.update_table()

            # Clear input fields
            self.newSymbol.clear()
            self.newPrice.clear()
            self.newPE.clear()
            self.newGroup.clear()

            QMessageBox.information(self, "Success", "New data added successfully.")
        except ValueError:
            QMessageBox.warning(self, "Input Error", "Price and PE must be numeric values.")

    def delete_data(self):
        # Requirement 7: Delete rows by Symbol
        symbol = self.deleteSymbol.text().strip()
        if not symbol:
            QMessageBox.warning(self, "Input Error", "Please enter a symbol to delete.")
            return

        initial_len = len(self.df)
        self.df = self.df[self.df['Symbol'] != symbol]

        if len(self.df) < initial_len:
            self.update_table()
            QMessageBox.information(self, "Success", f"Rows with Symbol {symbol} deleted.")
        else:
            QMessageBox.warning(self, "Not Found", f"Symbol {symbol} not found in the data.")

    def sort_by_price(self):
        # Requirement 2: Sort by Price ascending
        self.df = self.df.sort_values(by='Price')
        self.update_table()
        QMessageBox.information(self, "Success", "Data sorted by Price (ascending).")

    def calculate_stats(self):
        # Requirement 6: Group by Group column and calculate statistics
        stat_func = self.statsCombo.currentText()

        try:
            if stat_func == "mean":
                result = self.df.groupby('Group').mean()
            elif stat_func == "sum":
                result = self.df.groupby('Group').sum()
            elif stat_func == "count":
                result = self.df.groupby('Group').count()
            elif stat_func == "min":
                result = self.df.groupby('Group').min()
            elif stat_func == "max":
                result = self.df.groupby('Group').max()

            # Display results in a message box
            QMessageBox.information(self, f"Group {stat_func.capitalize()}",
                                    f"Results of {stat_func} by Group:\n\n{result}")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error calculating statistics: {e}")

    def generate_charts(self):
        # Clear previous charts
        self.figure.clear()

        # Create two subplots
        ax1 = self.figure.add_subplot(121)
        ax2 = self.figure.add_subplot(122)

        # Chart 1: Bar chart of prices by symbol
        ax1.bar(self.df['Symbol'], self.df['Price'])
        ax1.set_title('Price by Symbol')
        ax1.set_xlabel('Symbol')
        ax1.set_ylabel('Price')
        ax1.tick_params(axis='x', rotation=45)

        # Chart 2: Pie chart of group distribution
        group_counts = self.df['Group'].value_counts()
        ax2.pie(group_counts, labels=group_counts.index, autopct='%1.1f%%')
        ax2.set_title('Distribution by Group')

        self.figure.tight_layout()
        self.canvas.draw()

