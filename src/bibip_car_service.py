import os
from decimal import Decimal
from models import Car, CarFullInfo, CarStatus, Model, ModelSaleStats, Sale


class CarService:
    def __init__(self, root_directory_path: str) -> None:
        """Инициализирует объект класса CarService и устанавливает пути к необходимым файлам."""
        self.root_directory_path = root_directory_path
        """Пути сохранения файлов"""
        self.sale_path = os.path.join(self.root_directory_path, 'sales.txt')
        self.model_path = os.path.join(self.root_directory_path, 'models.txt')
        self.index_model = os.path.join(self.root_directory_path, 'models_index.txt')
        self.car_path = os.path.join(self.root_directory_path, 'cars.txt')
        self.index_car = os.path.join(self.root_directory_path, 'cars_index.txt')
        self.index_sell = os.path.join(self.root_directory_path, 'sales_index.txt')      
        """Счётчик строк для файлов с индексами."""
        self.count_index_model = 0
        self.count_index_car = 0
        self.count_index_sales = 0
        self.is_deleted = False # is_deleted (bool): Флаг, показывающий состояние удаления записи.


    def search_index(self, path, search_row):
        """Поиск номера строки в файле с индексом."""    
        with open(path, 'r', encoding='utf-8') as file_index:
            data_file = file_index.readlines()
            for data_files in data_file:
                parts_data = data_files.strip().split(',')
                key_row = parts_data[0].strip()
                index_row = int(parts_data[1].strip()) - 1 
                if 'cars_index.txt' in path and key_row == search_row:
                    return index_row
                elif 'models_index.txt' in path and index_row + 1 == search_row:
                    return index_row
                elif 'sales_index.txt' in path and search_row in key_row:
                     return index_row
        
                              
    def add_model(self, model: Model):
        """Добавление автомобилей и создание файла с индексами."""
        with open(self.model_path, mode='a', encoding='utf-8') as file_model, \
             open(self.index_model, 'a', encoding='utf-8') as file_index_model:                  
            file_model.write(f'{model.id}, {model.name}, {model.brand.ljust(500)}\n')
            self.count_index_model += 1
            file_index_model.write(f'{model.name}, {self.count_index_model}\n')


    def add_car(self, car: Car):
        """Добавление моделей и создание файла с индексами."""    
        with open(self.car_path, 'a', encoding='utf-8') as file_cars, \
             open(self.index_car, 'a', encoding='utf-8') as file_index_cars:
            file_cars.write(f'{car.vin}, {car.model}, {car.price}, {car.date_start}, {car.status.ljust(500)}\n')       
            self.count_index_car += 1
            file_index_cars.write(f'{car.vin}, {self.count_index_car}\n')


    def sell_car(self, sale: Sale):
        """Запись о продажах."""
        with open (self.sale_path, 'a', encoding='utf-8') as file_sales, \
             open(self.index_sell, 'a', encoding='utf-8') as file_index_sales:
            file_sales.write(f'{sale.sales_number}, {sale.car_vin}, {sale.sales_date}, {str(sale.cost).ljust(500)}\n')
            self.count_index_sales += 1            
            file_index_sales.write(f'{sale.sales_number}, {self.count_index_sales}\n')

        """Находим вин номер в файле продаж"""
        with open(self.index_sell, 'r', encoding='utf-8') as file_index_sales, \
             open(self.sale_path, 'r', encoding='utf-8') as file_sales:
            data_file_index_sales = file_index_sales.readlines()         
            for row_file_index_sales in data_file_index_sales:
                parts_row = row_file_index_sales.strip().split(',')
                sales_number_index_file = parts_row[0].strip()
                row_number_index_file = int(parts_row[1].strip()) - 1
                if sales_number_index_file == sale.sales_number:
                    file_sales.seek(row_number_index_file * (501))
                    row_file_sales = file_sales.read(500).strip().split(',')
                    vin_file_sales = row_file_sales[1].strip() # Vin из файла с продажами
                    break
              
        """Находим строку в файле cars с проданным авто""" 
        with open(self.index_car, 'r', encoding='utf-8') as file_index_cars, \
             open(self.car_path, 'r+', encoding='utf-8') as file_cars:
            data_file_index_cars = file_index_cars.readlines()
            for row_index_file in data_file_index_cars:
                parst_row_index_file = row_index_file.strip().split(',')
                vin_index_file = parst_row_index_file[0].strip()
                if vin_index_file == vin_file_sales:
                    row_number_index_car = int(parst_row_index_file[1].strip()) - 1 
                    file_cars.seek(row_number_index_car * (501)) 
                    row_file_cars = file_cars.read(500).strip().split(',')
                    """Собираем обьект с новым статусом"""
                    new_car_status = Car(
                        vin=row_file_cars[0].strip(),
                        model=row_file_cars[1].strip(),
                        price=row_file_cars[2].strip(),
                        date_start=row_file_cars[3].strip(),
                        status='sold'.strip()   
                    )
                    """Перезапись новой строки
                       row_number_index_car: Номер строки.
                       Если строка самая первая то не ставим \n.
                    """
                    formatted_new_car_data = f'{new_car_status.vin}, {new_car_status.model}, {new_car_status.price}, {new_car_status.date_start}, {new_car_status.status}'
                    file_cars.seek(row_number_index_car * 501)
                    if row_number_index_car == 0:  
                       file_cars.write(f'{formatted_new_car_data.ljust(500)}')
                    else:  
                        file_cars.write(f'\n{formatted_new_car_data.ljust(500)}')
            
                       
    def get_cars(self, status: CarStatus) -> list[Car]:
        """Вывод машин, доступных к продаже."""
        available_cars = []
        with open(self.car_path, 'r', encoding='utf-8') as file_cars:
            for row_file_cars in file_cars:            
                file_cars = row_file_cars.strip().split(',')
                car_status = file_cars[-1].strip()
                if car_status == 'available':
                    car_data = {
                        "vin": file_cars[0].strip(),
                        "model": int(file_cars[1]),
                        "price": file_cars[2].strip(),
                        "date_start": file_cars[3].strip(),
                        "status": CarStatus(file_cars[4].strip()),
                    }
                    available_cars.append(Car(**car_data))
            return available_cars
        

    def get_car_info(self, vin: str):  
        """Вывод информацию о машине по VIN-коду."""
        row_index_car = self.search_index(self.index_car, vin) # Индекс авто.
        if row_index_car is None: return None
        else: pass

        """Читаем данные по индексу в cars"""
        with open(self.car_path, 'r', encoding='utf-8') as file_cars:
            file_cars.seek(row_index_car * 501)
            file_car_part = file_cars.read(500).strip().split(',')
            vin_car = file_car_part[0].strip() # vin для вывода инфы.
            price = file_car_part[2].strip() # price для вывода инфы.
            date_start = file_car_part[3].strip() # date_start для вывода инфы.
            status = file_car_part[-1].strip() # status для вывода инфы.
            model_id = int(file_car_part[1].strip())

        row_index_model = self.search_index(self.index_model, model_id) # Индекс модели.

        """Читаем данные по индексу в models""" 
        with open(self.model_path, 'r', encoding='utf-8') as file_models:
            file_models.seek(row_index_model * 501)
            file_models_part = file_models.read(500).strip().split(',')
            model_name = file_models_part[1].strip() # model_name для вывода инфы.
            model_brand = file_models_part[2].strip() # model_brand для вывода инфы.

        
        if status != 'sold': # Автомобили которые еще не продали.
            join_data = ''.join(f'{vin_car}, {model_name}, {model_brand}, {price}, {date_start}, {status}').split(',')
            available_data = CarFullInfo(
                        vin=join_data[0].strip(),
                        car_model_name=join_data[1].strip(),
                        car_model_brand=join_data[2].strip(),
                        price=join_data[3].strip(),
                        date_start=join_data[4].strip(),
                        status=CarStatus(join_data[5].strip()),
                        sales_date=None,
                        sales_cost=None
                )
            return available_data     
        else: # Автомобили которые продали.
            row_index_sale = self.search_index(self.index_sell, vin_car)
            with open(self.sale_path, 'r', encoding='utf-8') as file_sales:
                file_sales.seek(row_index_sale * (501))
                file_sale_part = file_sales.read(500).strip().split(',')
                sales_date = file_sale_part[2].strip() # sales_date для вывода инфы.
                sales_cost = file_sale_part[-1].strip() # sales_cost для вывода инфы.
                join_data = ''.join(f'{vin_car}, {model_name}, {model_brand}, {price}, {date_start}, {status}, {sales_date}, {sales_cost}').split(',')
                sold_data = CarFullInfo(
                        vin=join_data[0].strip(),
                        car_model_name=join_data[1].strip(),
                        car_model_brand=join_data[2].strip(),
                        price=join_data[3].strip(),
                        date_start=join_data[4].strip(),
                        status=CarStatus(join_data[5].strip()),
                        sales_date=join_data[6].strip(),
                        sales_cost=join_data[7].strip()
                )
            return sold_data
   
                                 
    def update_vin(self, vin: str, new_vin: str) -> Car:
        """Перезапись VIN-кода на корректный."""
        row_index_car = self.search_index(self.index_car, vin)
        pass
        # with open(self.index_car, 'r', encoding='utf-8') as f:
        #     lines = f.readlines()
        #     for i in lines:
        #         parts_vin = i.strip().split(',')
        #         if vin == parts_vin[0]:
        #             row_number = int(parts_vin[1]) - 1
        #             with open(self.car_path, 'r+', encoding='utf-8') as f:
        #                  lines = f.readlines()
        #                  parts = lines[row_number].strip().split(',')
        #                  parts[0] = new_vin  
        #                  lines[row_number] = ','.join(parts) + '\n'  
        #                  f.seek(0)
        #                  f.writelines(lines)
        #                  f.truncate() 

        #             with open(self.index_car, 'r+', encoding='utf-8') as f:
        #                  lines = f.readlines()
        #                  parts_vin = i.strip().split(',')
        #                  parts = lines[row_number].strip().split(',')
        #                  parts[0] = new_vin  
        #                  lines[row_number] = ','.join(parts) + '\n'  
        #                  f.seek(0)
        #                  f.writelines(lines)
        #                  f.truncate() 


    def revert_sale(self, sales_number: str) -> Car:
        """Удаление записи из таблицы продаж и замена статуса для машины."""
        with open(self.index_sell, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            for i in lines:
                parts = i.strip().split(',')
                if parts[0] == sales_number:
                    row_index_sales = int(parts[1]) - 1
                    break
            else:
                return None
        
        with open(self.sale_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            sale_number = lines[row_index_sales].strip().split(',')
            vin = sale_number[1].strip()
            if sale_number[0] == sales_number and self.is_deleted == False:
                self.is_deleted = True

                with open(self.index_car, 'r', encoding='utf-8') as f:
                    all_lines = f.readlines()                   
                    for i in all_lines:
                        parts = i.strip().split(',')
                        current_vin = parts[0].strip()           
                        if vin == current_vin:
                            row_number = int(parts[1].strip()) - 1
                        break
          
                with open(self.car_path, 'r+', encoding='utf-8') as f:
                    all_lines = f.readlines()
                    parts = all_lines[row_number].strip().split(',')
                    parts[-1] = ' available'  
                    all_lines[row_number] = ','.join(parts) + '\n'  
                    f.seek(0)
                    f.writelines(all_lines)
                    f.truncate() 
            
                 
    def top_models_by_sales(self) -> list[ModelSaleStats]: 
        """Вывод самых продаваемых моделей"""    
        sales_stats: dict[int, int] = {}
        vin_to_model: dict[str, int] = {}

        with open(self.car_path, 'r', encoding='utf-8') as cars_file:
            for line in cars_file:
                parts = line.strip().split(',')
                vin_to_model[parts[0]] = int(parts[1])

        with open(self.sale_path, 'r', encoding='utf-8') as sales_file:
            for line in sales_file:
                parts = line.strip().split(',')
                vin = parts[1].strip()  
                if vin in vin_to_model:
                    model_id = vin_to_model[vin]
                    sales_stats[model_id] = sales_stats.get(model_id, 0) + 1
                else:
                    print(f"Внимание! VIN '{vin}' не найден в файле cars.txt")

        model_prices: dict[int, Decimal] = {}

        with open(self.car_path, 'r', encoding='utf-8') as cars_file:
            for line in cars_file:
                parts = line.strip().split(',')
                model_id = int(parts[1])
                price = Decimal(parts[2])
                if model_id not in model_prices or price > model_prices[model_id]:
                    model_prices[model_id] = price

        sorted_models: list[int] = sorted(
            sales_stats.keys(),
            key=lambda x: (-sales_stats[x], -model_prices.get(x, Decimal(0)))
        )[:3]

        result = []
        model_index = {}

        if os.path.exists(self.index_model):
            with open(self.index_model, 'r', encoding='utf-8') as index_file:
                for line in index_file:
                    parts = line.strip().split(',')
                    model_index[parts[0]] = int(parts[1])

        with open(self.model_path, 'r', encoding='utf-8') as models_file:
            models_data = models_file.readlines()
        for model_id in sorted_models:
            model_data = None
            if model_data is None:
                for line in models_data:
                    parts = line.strip().split(',')
                    if len(parts) >= 3 and int(parts[0]) == model_id:
                        model_data = line.strip()
                        break
                parts = model_data.split(',')
                if len(parts) >= 3:
                    result.append(ModelSaleStats(
                        car_model_name=parts[1].strip(),
                        brand=parts[2].strip(),
                        sales_number=sales_stats[model_id]
                    ))
        return result


        
        
        
            
            
        
                    
             
        
            
                
                    
            
                
                    
                
            
                
                

            
            
            
                
                
                        
                        
            


        