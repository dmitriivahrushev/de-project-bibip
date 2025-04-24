import os
from decimal import Decimal
from models import Car, CarFullInfo, CarStatus, Model, ModelSaleStats, Sale


class CarService:
    def __init__(self, root_directory_path: str) -> None:
        """Инициализирует объект класса CarService и устанавливает пути к необходимым файлам."""
        self.root_directory_path = root_directory_path

        self.sale_path = os.path.join(self.root_directory_path, 'sales.txt')
        self.model_path = os.path.join(self.root_directory_path, 'models.txt')
        self.index_model = os.path.join(self.root_directory_path, 'models_index.txt')
        self.car_path = os.path.join(self.root_directory_path, 'cars.txt')
        self.index_car = os.path.join(self.root_directory_path, 'cars_index.txt')
        self.index_sell = os.path.join(self.root_directory_path, 'sales_index.txt')

        self.is_deleted = False # is_deleted (bool): Флаг, показывающий состояние удаления записи.
        """Счётчик строк для файлов с индексами."""
        self.count_index_model = 0
        self.count_index_car = 0

    def add_model(self, model: Model) -> Model:
        """Добавление автомобилей и создание файла с индексами."""    
        with open(self.model_path, mode='a', encoding='utf-8') as file_model, \
             open(self.index_model, 'a', encoding='utf-8') as file_index_model:                  
            file_model.write(f'{model.id}, {model.name}, {model.brand.ljust(500)}\n')
            self.count_index_model += 1
            file_index_model.write(f'{model.name}, {self.count_index_model}\n')
            
        
    def add_car(self, car: Car) -> Car:
        """Добавление моделей и создание файла с индексами."""    
        with open(self.car_path, 'a', encoding='utf-8') as file_cars, \
             open(self.index_car, 'a', encoding='utf-8') as file_index_cars:
            file_cars.write(f'{car.vin}, {car.model}, {car.price}, {car.date_start}, {car.status.ljust(500)}\n')       
            self.count_index_car += 1
            file_index_cars.write(f'{car.vin}, {self.count_index_car}\n')
        
        
    def sell_car(self, sale: Sale) -> Car:
        """Запись о продажах."""
        with open (self.sale_path, 'a', encoding='utf-8') as f:
            f.write(f'{sale.sales_number}, {sale.car_vin}, {sale.sales_date}, {sale.cost}\n')
            
        with open(self.index_sell, 'a', encoding='utf-8') as f:
            num_lines = sum(1 for _ in open(self.sale_path, 'r', encoding='utf-8'))
            f.write(f'{sale.sales_number}, {num_lines}\n')

        with open(self.index_sell, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            row_number = lines[0].split(',')
            row_val = int(row_number[1].strip()) - 1  

        with open(self.sale_path, 'r', encoding='utf-8') as f:
            all_lines = f.readlines()
            parts = all_lines[row_val].strip().split(',')
            vin = parts[1].strip()

        with open(self.index_car, 'r', encoding='utf-8') as f:
            all_lines = f.readlines()
            for i in all_lines:
                parts = i.strip().split(',')
                current_vin = parts[0].strip()               
                if vin == current_vin:
                    row_number = int(parts[1].strip()) - 1
         
        with open(self.car_path, 'r+', encoding='utf-8') as f:
            all_lines = f.readlines()
            parts = all_lines[row_number].strip().split(',')
            parts[-1] = ' sold'  # Меняем статус на "sold"
            all_lines[row_number] = ','.join(parts) + '\n'  
            f.seek(0)
            f.writelines(all_lines)
            f.truncate() 
          
    
    def get_cars(self, status: CarStatus) -> list[Car]:
        """Вывод машин, доступных к продаже."""
        raw_cars = []
        with open(self.car_path, 'r', encoding='utf-8') as f:
            for i in f:            
                parts = i.strip().split(',')
                if parts[-1].strip() == 'available':
                    raw_cars.append(parts)

        available_cars = []
        for raw_item in raw_cars:
            car_data = {
                "vin": raw_item[0],
                "model": int(raw_item[1]),
                "price": raw_item[2],
                "date_start": raw_item[3].strip(),
                "status": CarStatus(raw_item[4].strip()),
                }
            available_cars.append(Car(**car_data))
        return available_cars


    def get_car_info(self, vin: str) -> CarFullInfo | None:  
        """Вывод информацию о машине по VIN-коду."""
        with open(self.index_car, 'r', encoding='utf-8') as f:
            lines = f.readlines()        
            for i in lines:
                parts = i.strip().split(',')    
                if vin == parts[0]:
                    row_index_car = (int(parts[1]))
                    break
            else:
                return None     
   
        with open(self.car_path, 'r', encoding='utf-8') as f_cars, \
             open(self.model_path, 'r', encoding='utf-8') as f_model:
            
            f_model_lines = f_model.readlines()
            f_cars_lines = f_cars.readlines()
            search_parts_f_cars = f_cars_lines[row_index_car - 1].strip().split(',') 
            key_model = int(search_parts_f_cars[1])
            status_part = search_parts_f_cars[-1].strip()
            search_parts_f_model = f_model_lines[key_model - 1] 
                     
            if status_part != 'sold':             
                join_info_sold = ','.join(search_parts_f_cars + [search_parts_f_model]).split(',')                            
                available_data = CarFullInfo(
                        vin=join_info_sold[0].strip(),
                        car_model_name=join_info_sold[6].strip(),
                        car_model_brand=join_info_sold[7].strip(),
                        price=join_info_sold[2].strip(),
                        date_start=join_info_sold[3].strip(),
                        status=CarStatus(join_info_sold[4].strip()),
                        sales_date=None,
                        sales_cost=None
                )
                return available_data
            else:   
                with open(self.sale_path, 'r', encoding='utf-8') as f_sales:
                    f_sales_lines = f_sales.readlines()
                    join_info_sold = ','.join(search_parts_f_cars + [search_parts_f_model]).split(',') 
                    sold_raw_data = ','.join(join_info_sold + f_sales_lines).split(',')
                    sold_data = CarFullInfo(
                        vin=sold_raw_data[0].strip(),
                        car_model_name=sold_raw_data[6].strip(),
                        car_model_brand=sold_raw_data[7].strip(),
                        price=sold_raw_data[2].strip(),
                        date_start=sold_raw_data[3].strip(),
                        status=CarStatus(sold_raw_data[4].strip()),
                        sales_date=sold_raw_data[-2].strip(),
                        sales_cost=sold_raw_data[-1].strip()
                    )
                    return sold_data
                
                    
    def update_vin(self, vin: str, new_vin: str) -> Car:
        """Перезапись VIN-кода на корректный."""
        with open(self.index_car, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            for i in lines:
                parts_vin = i.strip().split(',')
                if vin == parts_vin[0]:
                    row_number = int(parts_vin[1]) - 1
                    with open(self.car_path, 'r+', encoding='utf-8') as f:
                         lines = f.readlines()
                         parts = lines[row_number].strip().split(',')
                         parts[0] = new_vin  
                         lines[row_number] = ','.join(parts) + '\n'  
                         f.seek(0)
                         f.writelines(lines)
                         f.truncate() 

                    with open(self.index_car, 'r+', encoding='utf-8') as f:
                         lines = f.readlines()
                         parts_vin = i.strip().split(',')
                         parts = lines[row_number].strip().split(',')
                         parts[0] = new_vin  
                         lines[row_number] = ','.join(parts) + '\n'  
                         f.seek(0)
                         f.writelines(lines)
                         f.truncate() 


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


        
        
        
            
            
        
                    
             
        
            
                
                    
            
                
                    
                
            
                
                

            
            
            
                
                
                        
                        
            


        