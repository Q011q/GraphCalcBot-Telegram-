from telegram import Update, ReplyKeyboardMarkup  # Импортируем необходимые классы для работы с Telegram API
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters  # Импортируем компоненты для создания бота
import numpy as np  # Импортируем NumPy для работы с числовыми массивами
import matplotlib.pyplot as plt  # Импортируем matplotlib для построения графиков
from mpl_toolkits.mplot3d import Axes3D  # Импортируем 3D графику для matplotlib
import os  # Импортируем библиотеку для работы с файловой системой
from sympy import sympify, symbols  # Импортируем sympy для безопасной обработки математических выражений

# Главная клавиатура, которая отображает выбор между 2D и 3D графиками
main_keyboard = ReplyKeyboardMarkup([
    ['2D Графика', '3D Графика'],
    ['Помощь']
], resize_keyboard=True)  # Указываем, что кнопки должны быть адаптированы по размеру

# Клавиатура для выбора типа 2D графиков (явная или неявная функция)
keyboard_2d = ReplyKeyboardMarkup([
    ['Добавить Явную Функцию', 'Добавить Неявную Функцию'],
    ['Очистить', 'Назад']
], resize_keyboard=True)

# Клавиатура для выбора типа 3D графиков (только одна функция — 3D функция)
keyboard_3d = ReplyKeyboardMarkup([
    ['Добавить 3D Функцию'],
    ['Назад']
], resize_keyboard=True)

# Функция помощи, которая отправляет инструкции по использованию бота
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда помощи"""
    await update.message.reply_text(
        "Команды:\n"
        "- /start: Запуск бота\n"
        "- /help: Получить помощь\n"
        "- Используйте кнопки для работы с графиками."
    )

# Функция, которая вызывается при запуске бота
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Стартовая команда"""
    await update.message.reply_text(
        "Привет! Это бот для построения графиков. Выберите категорию:",
        reply_markup=main_keyboard
    )

# Обработчик для меню 2D графиков
async def handle_2d_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик меню 2D графики"""
    await update.message.reply_text("Вы выбрали 2D графику. Что хотите сделать?", reply_markup=keyboard_2d)

# Обработчик для меню 3D графиков
async def handle_3d_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик меню 3D графики"""
    await update.message.reply_text("Вы выбрали 3D графику. Что хотите сделать?", reply_markup=keyboard_3d)

# Функция для очистки графиков
async def handle_clear(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Очистка графиков"""
    await update.message.reply_text("График очищен. Вы можете добавить новые функции.")

# Функция для возврата в главное меню
async def handle_back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Возврат в главное меню"""
    await update.message.reply_text("Вы вернулись в главное меню.", reply_markup=main_keyboard)

# Функция для добавления явной функции (например, y = x**2)
async def add_explicit_function(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Добавление явной функции"""
    await update.message.reply_text("Введите явную функцию в формате: y = x**2 или y = sin(x).")
    context.user_data['state'] = 'add_explicit'  # Сохраняем состояние пользователя, чтобы понять, какую функцию он хочет ввести

# Функция для добавления неявной функции (например, x**2 + y**2 = 1)
async def add_implicit_function(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Добавление неявной функции"""
    await update.message.reply_text("Введите неявную функцию в формате: x**2 + y**2 - 1 = 0.")
    context.user_data['state'] = 'add_implicit'  # Сохраняем состояние для обработки неявной функции

# Функция для добавления 3D функции (например, z = sin(x)*cos(y))
async def add_3d_function(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Добавление 3D функции"""
    await update.message.reply_text("Введите 3D функцию в формате: z = sin(x) * cos(y).")
    context.user_data['state'] = 'add_3d'  # Сохраняем состояние для обработки 3D функции

# Обработчик для получения введенной функции и построения графика
async def handle_function_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка пользовательского ввода для 2D и 3D функции"""
    state = context.user_data.get('state')  # Получаем текущее состояние пользователя

    # Если состояние пустое, то пользователь не выбрал тип графика
    if state is None:
        await update.message.reply_text("Сначала выберите тип графика, например, '2D Графика' или '3D Графика'.")
        return

    try:
        # Обработка явной функции y = f(x)
        if state == 'add_explicit':
            equation = update.message.text.replace('y =', '').strip()  # Получаем функцию из сообщения

            # Используем sympy для безопасной обработки математических выражений
            x = symbols('x')
            expr = sympify(equation)  # Преобразуем строку в математическое выражение
            y = np.array([float(expr.subs(x, xi)) for xi in np.linspace(-10, 10, 400)])  # Вычисляем значения функции

            # Строим график
            plt.figure()
            plt.plot(np.linspace(-10, 10, 400), y, label=f"y = {equation}")
            plt.legend()
            plt.title("Явная функция")
            plt.xlabel('X')
            plt.ylabel('Y')
            plt.grid()

            file_path = "explicit_plot.png"  # Указываем путь для сохранения графика
            plt.savefig(file_path)  # Сохраняем график
            plt.close()  # Закрываем график

            # Отправляем график пользователю
            await update.message.reply_photo(photo=open(file_path, 'rb'))

        # Обработка неявной функции x**2 + y**2 = 1
        elif state == 'add_implicit':
            equation = update.message.text.strip()  # Получаем неявную функцию
            x = np.linspace(-10, 10, 400)  # Массив значений для x
            y = np.linspace(-10, 10, 400)  # Массив значений для y
            X, Y = np.meshgrid(x, y)  # Создаем сетку значений

            # Преобразуем неявную функцию в Z (например, круг радиуса 1)
            Z = X**2 + Y**2 - 1

            # Строим контурный график
            plt.figure()
            cp = plt.contour(X, Y, Z, levels=[0], colors='blue')  # Контур уровня 0 (круг)
            plt.title(f"Неявная функция: {equation}")
            plt.xlabel('X')
            plt.ylabel('Y')
            plt.grid()

            file_path = "implicit_plot.png"  # Указываем путь для сохранения графика
            plt.savefig(file_path)  # Сохраняем график
            plt.close()  # Закрываем график

            # Отправляем график пользователю
            await update.message.reply_photo(photo=open(file_path, 'rb'))

        # Обработка 3D функции (например, z = sin(x) * cos(y))
        elif state == 'add_3d':
            equation = update.message.text.strip()  # Получаем 3D функцию
            x = np.linspace(-10, 10, 400)  # Массив значений для x
            y = np.linspace(-10, 10, 400)  # Массив значений для y
            X, Y = np.meshgrid(x, y)  # Создаем сетку значений

            # Пример добавления 3D функции
            if equation == "z = cos(x) * sin(y)":
                Z = np.cos(X) * np.sin(Y)  # Вычисляем значения Z для функции cos(x) * sin(y)
            elif equation == "z = sin(sqrt(x**2 + y**2))":
                Z = np.sin(np.sqrt(X**2 + Y**2))  # Вычисляем для функции sin(sqrt(x^2 + y^2))
            elif equation == "z = sqrt(100 - x**2 - y**2)":  # Пример сферы
                Z = np.sqrt(100 - X**2 - Y**2)
                Z = np.nan_to_num(Z, nan=np.nan)  # Обработка NaN для точек, где x^2 + y^2 > 100
            else:
                await update.message.reply_text("Неизвестная функция. Попробуйте другую.")
                return

            # Строим 3D график
            fig = plt.figure()
            ax = fig.add_subplot(111, projection='3d')
            ax.plot_surface(X, Y, Z, cmap='viridis')  # Строим поверхность

            ax.set_title(f"3D график: {equation}")  # Заголовок графика
            ax.set_xlabel('X')
            ax.set_ylabel('Y')
            ax.set_zlabel('Z')

            file_path = "3d_plot.png"  # Указываем путь для сохранения графика
            plt.savefig(file_path)  # Сохраняем график
            plt.close()  # Закрываем график

            # Проверяем, существует ли файл
            if os.path.exists(file_path):
                await update.message.reply_photo(photo=open(file_path, 'rb'))
            else:
                await update.message.reply_text("Не удалось сохранить изображение.")

        # Завершаем состояние после обработки
        context.user_data['state'] = None
    
    except Exception as e:
        # Если возникла ошибка, отправляем пользователю сообщение
        await update.message.reply_text(f"Ошибка: {str(e)}")
        context.user_data['state'] = None

# Обработчик для неизвестных команд
async def handle_unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик неизвестных команд"""
    await update.message.reply_text("Я не понимаю эту команду. Попробуйте снова.")

# Главная функция для запуска бота
def main():
    # Создаем экземпляр приложения с токеном бота
    application = ApplicationBuilder().token("7233616501:AAFVBYD4KPNzgSfJg2RB2-t3PGNYuXvGMt8").build()

    # Основные команды
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))

    # Обработчики сообщений
    application.add_handler(MessageHandler(filters.Regex('^2D Графика$'), handle_2d_menu))
    application.add_handler(MessageHandler(filters.Regex('^3D Графика$'), handle_3d_menu))
    application.add_handler(MessageHandler(filters.Regex('^Назад$'), handle_back))
    application.add_handler(MessageHandler(filters.Regex('^Очистить$'), handle_clear))
    application.add_handler(MessageHandler(filters.Regex('^Добавить Явную Функцию$'), add_explicit_function))
    application.add_handler(MessageHandler(filters.Regex('^Добавить Неявную Функцию$'), add_implicit_function))
    application.add_handler(MessageHandler(filters.Regex('^Добавить 3D Функцию$'), add_3d_function))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_function_input))

    # Обработчик неизвестных команд
    application.add_handler(MessageHandler(filters.COMMAND, handle_unknown))

    # Запуск бота
    application.run_polling()

if __name__ == "__main__":
    main()
