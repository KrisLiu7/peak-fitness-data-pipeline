import streamlit as st
import pandas as pd
from pyathena import connect
import matplotlib.pyplot as plt
import plotly.express as px

st.title("Peak Fitness Analytics Dashboard")

# Athena connection
try:
    conn = connect(
        s3_staging_dir="s3://peak-fitness-athena-results/",
        region_name="us-east-1",
        schema_name="peak_fitness"
    )

    # Sidebar Navigation
    st.sidebar.title("Leaderboard Sections")
    selection = st.sidebar.selectbox("Choose an analysis:", [
        "Monthly Attendance",
        "Top 5 Locations",
        "Churn by Instructor",
        "Churn by Location",
        "Weighted Class Popularity",
        "New User First Class",
        "New User Class Transition Behavior",
        "Retention Trend: Class Type Diversity",
        "Heatmap: Location Attendance"
    ])

    ### 🔹 Monthly Attendance Trend
    if selection == "Monthly Attendance":
        st.subheader("📅 Monthly Attendance Trend")
        query = """
        SELECT 
            year(from_unixtime(class_datetime / 1000)) AS year,
            month(from_unixtime(class_datetime / 1000)) AS month,
            SUM(attendance_count) AS total_attendance
        FROM class_attendance
        GROUP BY year(from_unixtime(class_datetime / 1000)), month(from_unixtime(class_datetime / 1000))
        ORDER BY year(from_unixtime(class_datetime / 1000)), month(from_unixtime(class_datetime / 1000));
        """
        try:
            df = pd.read_sql(query, conn)
            df["label"] = df["year"].astype(str) + "-" + df["month"].astype(str).str.zfill(2)
            fig, ax = plt.subplots()
            ax.plot(df["label"], df["total_attendance"], marker="o")
            ax.set_xlabel("Month")
            ax.set_ylabel("Total Attendance")
            plt.xticks(rotation=45)
            st.pyplot(fig)
        except Exception as e:
            st.error(f"Error executing query: {str(e)}")
            st.code(query, language="sql")

    ### 🔹 Top 5 Locations by Session Count
    elif selection == "Top 5 Locations":
        st.subheader("🏆 Top 5 Locations by Number of Sessions")
        top_locations_query = """
        SELECT dl.location_name, COUNT(*) AS session_count
        FROM dim_classes dc
        JOIN dim_locations dl ON dc.location_id = dl.location_id
        GROUP BY dl.location_name
        ORDER BY session_count DESC
        LIMIT 5;
        """
        try:
            top_locations_df = pd.read_sql(top_locations_query, conn)
            st.dataframe(top_locations_df)
            fig, ax = plt.subplots()
            ax.bar(top_locations_df["location_name"], top_locations_df["session_count"])
            ax.set_xlabel("Location Name")
            ax.set_ylabel("Number of Sessions")
            plt.xticks(rotation=45)
            st.pyplot(fig)
        except Exception as e:
            st.error(f"Failed to load top locations: {str(e)}")
            st.code(top_locations_query, language="sql")

    ### 🔹 Churn Rate by Instructor
    elif selection == "Churn by Instructor":
        st.subheader("📉 Churn Rate by Instructor")
        churn_query = """
        WITH user_months AS (
            SELECT
                json_extract_scalar(CAST(attendee AS JSON), '$.user_id') AS user_id,
                instructor_name,
                date_trunc('month', from_unixtime(class_datetime / 1000)) AS activity_month
            FROM class_attendance
            CROSS JOIN UNNEST(attendees) AS t(attendee)
        ),
        user_activity_span AS (
            SELECT
                user_id,
                instructor_name,
                COUNT(DISTINCT activity_month) AS active_months,
                MAX(activity_month) AS last_month
            FROM user_months
            GROUP BY user_id, instructor_name
        )
        SELECT
            instructor_name,
            COUNT(*) AS churned_users
        FROM user_activity_span
        WHERE active_months = 1
        GROUP BY instructor_name
        ORDER BY churned_users DESC
        LIMIT 5;
        """
        try:
            churn_df = pd.read_sql(churn_query, conn)
            st.dataframe(churn_df)
            fig, ax = plt.subplots()
            ax.bar(churn_df["instructor_name"], churn_df["churned_users"])
            ax.set_xlabel("Instructor Name")
            ax.set_ylabel("Churned Users")
            plt.xticks(rotation=45)
            st.pyplot(fig)
        except Exception as e:
            st.error(f"Failed to load churn data: {str(e)}")
            st.code(churn_query, language="sql")

    ### 🔹 Churn Rate by Location
    elif selection == "Churn by Location":
        st.subheader("📉 Churn Rate by Location")
        churn_location_query = """
        WITH user_months AS (
            SELECT
                json_extract_scalar(CAST(attendee AS JSON), '$.user_id') AS user_id,
                location_id,
                date_trunc('month', from_unixtime(class_datetime / 1000)) AS activity_month
            FROM class_attendance
            CROSS JOIN UNNEST(attendees) AS t(attendee)
        ),
        user_activity_span AS (
            SELECT
                user_id,
                location_id,
                COUNT(DISTINCT activity_month) AS active_months,
                MAX(activity_month) AS last_month
            FROM user_months
            GROUP BY user_id, location_id
        )
        SELECT
            location_id,
            COUNT(*) AS churned_users
        FROM user_activity_span
        WHERE active_months = 1
        GROUP BY location_id
        ORDER BY churned_users DESC
        LIMIT 5;
        """
        try:
            churn_loc_df = pd.read_sql(churn_location_query, conn)
            st.dataframe(churn_loc_df)
            fig, ax = plt.subplots()
            ax.bar(churn_loc_df["location_id"], churn_loc_df["churned_users"])
            ax.set_xlabel("Location ID")
            ax.set_ylabel("Churned Users")
            plt.xticks(rotation=45)
            st.pyplot(fig)
        except Exception as e:
            st.error(f"Failed to load churn data: {str(e)}")
            st.code(churn_location_query, language="sql")

    ### 🔹 Weighted Class Popularity
    elif selection == "Weighted Class Popularity":
        st.subheader("📊 Weighted Class Popularity")
        weighted_query = """
        WITH attendance AS (
            SELECT
                class_name,
                SUM(attendance_count) AS total_attendance
            FROM class_attendance
            GROUP BY class_name
        ),
        sessions AS (
            SELECT
                class_name,
                COUNT(*) AS total_sessions
            FROM dim_classes
            GROUP BY class_name
        ),
        totals AS (
            SELECT
                SUM(total_attendance) OVER () AS grand_attendance,
                SUM(total_sessions) OVER () AS grand_sessions
            FROM attendance
            JOIN sessions USING (class_name)
        )
        SELECT
            a.class_name,
            a.total_attendance,
            s.total_sessions,
            ROUND(a.total_attendance * 100.0 / t.grand_attendance, 2) AS attendance_pct,
            ROUND(s.total_sessions * 100.0 / t.grand_sessions, 2) AS session_pct,
            ROUND(a.total_attendance * 100.0 / t.grand_attendance - s.total_sessions * 100.0 / t.grand_sessions, 2) AS delta
        FROM attendance a
        JOIN sessions s ON a.class_name = s.class_name
        CROSS JOIN totals t
        ORDER BY delta DESC
        LIMIT 10;
        """
        try:
            weighted_df = pd.read_sql(weighted_query, conn)
            st.dataframe(weighted_df)
            fig, ax = plt.subplots()
            ax.bar(weighted_df["class_name"], weighted_df["delta"])
            ax.set_ylabel("Attendance% - Session% (Δ)")
            ax.set_xlabel("Class Name")
            plt.xticks(rotation=45)
            st.pyplot(fig)
        except Exception as e:
            st.error(f"Failed to load weighted class analysis: {str(e)}")
            st.code(weighted_query, language="sql")

    ### 🔹 New User First Class Type
    elif selection == "New User First Class":
        st.subheader("🧭 First Class Type Taken by New Users")
        new_user_query = """
        WITH flattened AS (
            SELECT 
                json_extract_scalar(CAST(attendee AS JSON), '$.user_id') AS user_id,
                class_name,
                from_unixtime(class_datetime / 1000) AS activity_time
            FROM class_attendance
            CROSS JOIN UNNEST(attendees) AS t(attendee)
        ),
        joined AS (
            SELECT 
                f.user_id,
                f.class_name,
                f.activity_time,
                u.created_at
            FROM flattened f
            JOIN dim_users u ON f.user_id = u.user_id
        ),
        ranked AS (
            SELECT *,
                ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY activity_time ASC) AS rn
            FROM joined
            WHERE activity_time >= created_at
        )
        SELECT class_name, COUNT(*) AS new_user_count
        FROM ranked
        WHERE rn = 1
        GROUP BY class_name
        ORDER BY new_user_count DESC
        LIMIT 10;
        """
        try:
            new_user_df = pd.read_sql(new_user_query, conn)
            st.dataframe(new_user_df)
            fig, ax = plt.subplots()
            ax.bar(new_user_df["class_name"], new_user_df["new_user_count"])
            ax.set_title("Top First Class Types for New Users")
            ax.set_ylabel("New User Count")
            ax.set_xlabel("Class Name")
            plt.xticks(rotation=45)
            st.pyplot(fig)
        except Exception as e:
            st.error(f"Failed to load new user journey data: {str(e)}")
            st.code(new_user_query, language="sql")

    ### 🔹 New User Class Transition Behavior
    elif selection == "New User Class Transition Behavior":
        st.subheader("🧭 Second Class Type Taken by New Users")
        transition_query = """
        WITH flattened AS (
            SELECT
                json_extract_scalar(CAST(attendee AS JSON), '$.user_id') AS user_id,
                class_name,
                from_unixtime(class_datetime / 1000) AS activity_time
            FROM class_attendance
            CROSS JOIN UNNEST(attendees) AS t(attendee)
        ),
        joined AS (
            SELECT
                f.user_id,
                f.class_name,
                f.activity_time,
                u.created_at
            FROM flattened f
            JOIN dim_users u ON f.user_id = u.user_id
        ),
        ranked AS (
            SELECT *,
                ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY activity_time ASC) AS rn
            FROM joined
            WHERE activity_time >= created_at
        )
        SELECT class_name, COUNT(*) AS second_class_count
        FROM ranked
        WHERE rn = 2
        GROUP BY class_name
        ORDER BY second_class_count DESC
        LIMIT 10;
        """
        try:
            second_df = pd.read_sql(transition_query, conn)
            st.dataframe(second_df)
            fig, ax = plt.subplots()
            ax.bar(second_df["class_name"], second_df["second_class_count"])
            ax.set_title("Top Second Class Types for New Users")
            ax.set_ylabel("User Count")
            ax.set_xlabel("Class Name")
            plt.xticks(rotation=45)
            st.pyplot(fig)
        except Exception as e:
            st.error(f"Failed to load class transition data: {str(e)}")
            st.code(transition_query, language="sql")

    ### 🔹 Retention Trend: Class Type Diversity
    elif selection == "Retention Trend: Class Type Diversity":
        st.subheader("📈 Retention Trend: Class Type Diversity")
        retention_query = """
        WITH flattened AS (
            SELECT
                json_extract_scalar(CAST(attendee AS JSON), '$.user_id') AS user_id,
                class_name,
                from_unixtime(class_datetime / 1000) AS activity_time
            FROM class_attendance
            CROSS JOIN UNNEST(attendees) AS t(attendee)
        ),
        joined AS (
            SELECT
                f.user_id,
                f.class_name,
                f.activity_time,
                u.created_at
            FROM flattened f
            JOIN dim_users u ON f.user_id = u.user_id
            WHERE activity_time >= created_at
        ),
        user_engagement AS (
            SELECT
                user_id,
                COUNT(DISTINCT class_name) AS class_type_count,
                COUNT(DISTINCT date_trunc('month', activity_time)) AS active_months
            FROM joined
            GROUP BY user_id
        )
        SELECT
            class_type_count,
            COUNT(*) AS user_count
        FROM user_engagement
        GROUP BY class_type_count
        ORDER BY class_type_count;
        """
        try:
            diversity_df = pd.read_sql(retention_query, conn)
            st.dataframe(diversity_df)
            fig, ax = plt.subplots()
            ax.plot(
                diversity_df["class_type_count"],
                diversity_df["user_count"],
                marker="o"
            )
            ax.set_title("Class Type Diversity per User")
            ax.set_xlabel("Number of Unique Class Types Attended")
            ax.set_ylabel("User Count")
            st.pyplot(fig)
        except Exception as e:
            st.error(f"Failed to load retention trend data: {str(e)}")
            st.code(retention_query, language="sql")


    ### 🔹 Retention Trend: Class Type Diversity
    elif selection == "Retention Trend: Class Type Diversity":
        st.subheader("📈 Retention Trend: Class Type Diversity")
        retention_query = """
        WITH flattened AS (
            SELECT
                json_extract_scalar(CAST(attendee AS JSON), '$.user_id') AS user_id,
                class_name,
                from_unixtime(class_datetime / 1000) AS activity_time
            FROM class_attendance
            CROSS JOIN UNNEST(attendees) AS t(attendee)
        ),
        joined AS (
            SELECT
                f.user_id,
                f.class_name,
                f.activity_time,
                u.created_at
            FROM flattened f
            JOIN dim_users u ON f.user_id = u.user_id
            WHERE activity_time >= created_at
        ),
        user_engagement AS (
            SELECT
                user_id,
                COUNT(DISTINCT class_name) AS class_type_count,
                COUNT(DISTINCT date_trunc('month', activity_time)) AS active_months
            FROM joined
            GROUP BY user_id
        )
        SELECT
            class_type_count,
            COUNT(*) AS user_count
        FROM user_engagement
        GROUP BY class_type_count
        ORDER BY class_type_count;
        """
        try:
            diversity_df = pd.read_sql(retention_query, conn)
            st.dataframe(diversity_df)
            fig, ax = plt.subplots()
            ax.plot(
                diversity_df["class_type_count"],
                diversity_df["user_count"],
                marker="o"
            )
            ax.set_title("Class Type Diversity per User")
            ax.set_xlabel("Number of Unique Class Types Attended")
            ax.set_ylabel("User Count")
            st.pyplot(fig)
        except Exception as e:
            st.error(f"Failed to load retention trend data: {str(e)}")
            st.code(retention_query, language="sql")

    ### 🔥 Heatmap: Location Attendance (NEW SECTION)
    elif selection == "Heatmap: Location Attendance":
        st.subheader("🔥 Attendance Heatmap by Location")
        
        location_query = """
        SELECT 
            l.location_id,
            l.location_name AS name,
            SUM(c.attendance_count) AS total_attendance
        FROM class_attendance c
        JOIN dim_locations l ON c.location_id = l.location_id
        GROUP BY l.location_id, l.location_name
        ORDER BY total_attendance DESC
        """
        
        try:
            location_df = pd.read_sql(location_query, conn)
            
            if not location_df.empty:
                # Create interactive geographic heatmap
                st.warning("No geographic coordinates found - showing simulated heatmap")

                # Generate fake coordinates based on location_id (for demo)
                import numpy as np
                np.random.seed(42)
                location_df['lat'] = 40 + location_df['location_id'].astype('category').cat.codes * 0.1
                location_df['lon'] = -100 + location_df['location_id'].astype('category').cat.codes * 0.5

                #Create the heatmap
                fig = px.density_mapbox(
                    location_df,
                    lat='lat',
                    lon='lon',
                    z='total_attendance',
                    hover_name='name',
                    hover_data=['total_attendance'],
                    radius=20,
                    center=dict(lat=45, lon=-95),  # Center on US/Canada
                    zoom=3,
                    mapbox_style="stamen-terrain",
                    title="Simulated Attendance Heatmap (Demo)",
                )
                
                st.plotly_chart(fig, use_container_width=True)

                # Show the actual data
                st.write("Location Attendance Data:")
                st.dataframe(location_df[['name', 'total_attendance']])

            else:
                st.watning("No location data available")
             
        except Exception as e:
            st.error(f"Failed to load location data: {str(e)}")
            st.code(location_query, language="sql")

except Exception as e:
    st.error(f"Connection or query setup error: {str(e)}")
