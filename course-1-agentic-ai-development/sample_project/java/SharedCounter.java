public class SharedCounter {

    private int count = 0;
    private boolean running = true;

    public void increment() {
        count++;
    }

    public void stop() {
        running = false;
    }

    public boolean isRunning() {
        return running;
    }

    public static void main(String[] args) throws InterruptedException {
        SharedCounter counter = new SharedCounter();
        Runnable task = () -> {
            for (int i = 0; i < 100_000; i++) {
                counter.increment();
            }
        };

        Thread t1 = new Thread(task);
        Thread t2 = new Thread(task);
        t1.start();
        t2.start();

        System.out.println("Final count: " + counter.count);
    }
}
