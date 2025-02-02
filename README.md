# Urban Sports New Courses

This project checks for new courses available on Urban Sports Club and sends notifications via Pushover.

## Prerequisites

- Python 3.x
- Docker
- GitHub account

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/your-username/urbansports-new-courses.git
    cd urbansports-new-courses
    ```

2. Install the required Python packages:
    ```sh
    pip install -r requirements.txt
    ```

3. Install Playwright and its dependencies:
    ```sh
    playwright install
    ```

## Environment Variables

Create a `.env` file in the root directory and add the following environment variables:

```env
EMAIL=your_email@example.com
PASSWORD=your_password
PUSHOVER_USER_KEY=your_pushover_user_key
PUSHOVER_API_TOKEN=your_pushover_api_token