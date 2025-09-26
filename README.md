# Employee-Delay_Dashboard_with_LangChain_Analysis
This repository contains the code and data for an interactive dashboard that visualizes and analyzes employee delay data. The project uses LangChain for analysis and Streamlit for the interface.

Project Overview :-
	This dashboard is designed to help managers and HR professionals understand trends and patterns in employee punctuality and the reason also where the issue lies. By using a combination of a dynamic dashboard and a powerful AI-powered analysis tool, it transforms raw JSON data into actionable insights. The core functionality includes:
	
		1. Insights: Integration with LangChain to analyze the data and provides detailed observations, areas of concern, and reasons for its findings.
		
		2. Interactive Interface: A dashboard built with Streamlit to display key metrics and charts, including average violation counts and issue rankings.
		
		3. Multi-Tabbed Analysis: The dashboard is structured with multiple tabs to provide different views of the analysis, from a high-level overview to a deep dive into each issue.
		4. Automated Ranking: It automatically ranks the top three most concerning delay issues based on a comprehensive analysis, not just raw numbers.

		5. Detailed Explanations: Get in-depth explanations on why a specific issue is concerning and the potential reasons behind it.

		6.Interactive Charts: Explore data distribution with a pie chart for average violations and a line chart for issue rankings.

Technologies Used:- 
	Python: The core programming language.
	Streamlit: For building the interactive web dashboard.
	Pandas: For data manipulation and processing.
	LangChain: For building the natural language processing pipeline.
	Plotly: For creating the interactive data visualizations.
	OpenAI(with OpenRouter): The language model provider used by LangChain for analysis.

Install dependencies:-
	```pip install -r requirements.txt```

Data:-
	The dashboard is designed to analyze weekly delay data in a JSON format. The JSON data contains the following keys: 'shift_id', 'total_employees', 'date', 'meal_break', 'hot_seat', 'shift_change', 'no_operator', 'refueling', and 'unscheduled_maintenance'.

Running the Dashboard:-
	```streamlit run app.py```

Usage:-
	Once the dashboard is running, you can:
	Upload your JSON data file using the file uploader on the page.
	Click the "Analyze Report" button to let the AI process the data and generate the dashboard.
	Use the tabs and sidebar filters to interact with the visualizations and detailed insights.

Contributing:-
	Contributions are welcome! Please feel free to open an issue or submit a pull request.
