import seaborn as sns
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import pandas as pd
import mpld3


_dwellings = {1.0: "Family House", 0.7: "Semidetached", 0.4: "Townhome", 0.0: "Apartment"}


class PlotGenerator:
    """
    A class that calculates dynamic plots for the results HTML page based on the user's input data.
    """
    def __init__(self, df, pred, actual_value, record) -> None:
        """
        Initializing class variables.

        :param df: (pandas.DataFrame)All the records from the 'Active_data' database collection.
        :param pred: (float)The predicted energy consumption value of the given record.
        :param actual_value: (float)The actual energy consumption value of the given record.
        :param record: (dict)The user input from HTML forms.
        """
        sns.set_palette(sns.color_palette("Spectral"))
        self.data_frame = df
        self.prediction = pred
        self.actual = actual_value
        self.record = record

        self.dtype = _dwellings[record['Dwelling Grade']]

        self.plot_slot1, self.patches = self.similar_dwellings_plot()
        self.plot_slot3 = self.all_dwellings_plot()

    def all_dwellings_plot(self) -> str:
        """
        Plots a dynamic bar plot that presents the mean energy consumption per Dwelling type using
        plotly library.

        :return: (str)A string that contains HTML code.
        """
        kwhs = pd.DataFrame(self.data_frame.groupby('Dwelling Grade').mean(numeric_only=True))["Kwh/day/m2"]
        Dwellings = ["Apartment", "Townhome", "Semidetached", "Family House"]

        fig = go.Figure()
        fig.add_trace(go.Bar(x=Dwellings, y=kwhs, marker=dict(color=["#9b0f00", "#c16434", "#dfa669", "#edc986"])))
        fig.update_layout(
            autosize=True,
            height=300,
            width=450,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=0, r=0, t=0, b=0),
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=False, anchor='x', title={"text": "Kwhs"}),
        )

        return fig.to_html(full_html=False, config={'displayModeBar': False})

    def similar_dwellings_plot(self) -> tuple:
        """
        Plots a dynamic distribution plot that presents the user input energy consumption in contrast to similar type
        dwelling consumptions. Uses matplotlib, seaborn and mpld3 libraries.

        :return: (tuple)A tuple containing a string with HTML code and a bool value that informs the HTML page what
        coloring system to use.
        """
        self.data_frame = pd.concat([self.data_frame, pd.DataFrame(self.record, index=[0])], ignore_index=True)
        distribution = \
            self.data_frame.loc[self.data_frame['Dwelling Grade'] == self.record['Dwelling Grade']][
                "Kwh/day/m2"]

        print(len(self.data_frame.loc[self.data_frame['Dwelling Grade'] == self.record['Dwelling Grade']]))

        x_range = (max(distribution) + 0.10*max(distribution)) - min(distribution)
        bin_size = x_range / 30

        fig, ax = plt.subplots(figsize=(4, 3))
        hist = sns.histplot(distribution, kde=True, binwidth=bin_size)
        ax.set_title("Distribution of electrical consumption of similar Dwellings")

        patches = hist.patches

        real_cons = self.actual

        in_same_bin = False
        for patch in patches:

            patch.set_fc('#9b0f00')
            if patch.get_x() <= real_cons <= patch.get_x() + patch.get_width():
                if patch.get_height() == 0:
                    patch.set_height(1)

                if self.prediction > real_cons:
                    patch.set_fc('#FEFEB4')
                    in_same_bin = True
                elif self.prediction <= real_cons <= self.prediction + ((self.prediction * 10) / 100):
                    patch.set_fc('#FEFEB4')
                    in_same_bin = True
                elif real_cons > self.prediction + ((self.prediction * 10) / 100):

                    patch.set_fc('#ffa600')

            elif patch.get_x() <= self.prediction <= patch.get_x() + patch.get_width() and \
                    real_cons > self.prediction + ((self.prediction * 10) / 100) and not in_same_bin:
                if patch.get_height() == 0:
                    patch.set_height(1)
                patch.set_fc('#FEFEB4')

        plt.ylabel("No of Dwellings")
        plt.xlabel(None)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.set_facecolor((0., 0., 0., 0.))

        return mpld3.fig_to_html(fig), in_same_bin
