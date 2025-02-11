import streamlit as st
import pandas as pd
from io import BytesIO

def process_file(uploaded_file):
    try:
        # Чтение файла
        df = pd.read_excel(uploaded_file, engine='openpyxl')
        
        # Проверка наличия необходимых колонок
        required_columns = ['TarrifCodeClear', 'PercentNumberClear', 'TarrifCodeTWS', 'PercentNumberTWS']
        if not all(col in df.columns for col in required_columns):
            st.error("Файл не содержит необходимых колонок!")
            return None

        # Основной цикл обработки
        for idx, row in df.iterrows():
            current_code = row['TarrifCodeClear']
            
            # Поиск совпадений в TarrifCodeTWS
            matches = df[df['TarrifCodeTWS'] == current_code]
            
            if not matches.empty:
                # Получаем все значения PercentNumberTWS для совпадений
                e_values = matches['PercentNumberTWS'].tolist()
                
                if len(e_values) == 1:
                    # Одно совпадение - проверяем значения
                    if row['PercentNumberClear'] != e_values[0]:
                        df.at[idx, 'PercentNumberClear'] = e_values[0]
                else:
                    # Несколько совпадений - считаем среднее
                    average = sum(e_values) / len(e_values)
                    df.at[idx, 'PercentNumberClear'] = average

        return df

    except Exception as e:
        st.error(f"Ошибка обработки файла: {str(e)}")
        return None

# Интерфейс
st.title("Обработка тарифных кодов")
uploaded_file = st.file_uploader("Загрузите XLSX файл", type="xlsx")

if uploaded_file:
    if st.button("Запуск сравнения"):
        with st.spinner("Идет обработка файла..."):
            processed_df = process_file(uploaded_file)
            
        if processed_df is not None:
            st.success("Обработка завершена!")
            
            # Создаем файл для скачивания
            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                processed_df.to_excel(writer, index=False)
            
            st.download_button(
                label="Скачать обработанный файл",
                data=output.getvalue(),
                file_name="processed_file.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            
            # Показать предпросмотр данных
            st.subheader("Предпросмотр данных")
            st.dataframe(processed_df.head())