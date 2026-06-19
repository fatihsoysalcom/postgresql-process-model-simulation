# PostgreSQL Process Model Simulation

This Python script simulates the core process architecture of PostgreSQL. It demonstrates how a central `Postmaster` process starts and manages multiple `Backend` processes, each handling a client connection. The example also illustrates the concept of shared memory, where backends can access and modify shared data structures like a buffer cache or transaction counter, mimicking PostgreSQL's internal workings to help build a mental model of its behavior.

## Language

`python`

## How to Run

Save the code as `main.py` and run it from your terminal:
`python main.py`

## Original Article

This example accompanies the Turkish article: [PostgreSQL Zihin Modelim Nihayet Oturdu: Derinlemesine Bir Bakış](https://fatihsoysal.com/blog/postgresql-zihin-modelim-nihayet-oturdu-derinlemesine-bir-bakis/).

## License

MIT — see [LICENSE](LICENSE).
