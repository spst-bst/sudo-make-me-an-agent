public class BankTransfer {

    private final Object lockA = new Object();
    private final Object lockB = new Object();
    private int balanceA = 1000;
    private int balanceB = 1000;

    public void transferAtoB(int amount) {
        synchronized (lockA) {
            synchronized (lockB) {
                balanceA -= amount;
                balanceB += amount;
            }
        }
    }

    public void transferBtoA(int amount) {
        synchronized (lockB) {
            synchronized (lockA) {
                balanceB -= amount;
                balanceA += amount;
            }
        }
    }

    public static void main(String[] args) throws InterruptedException {
        BankTransfer account = new BankTransfer();

        Thread t1 = new Thread(() -> {
            for (int i = 0; i < 1000; i++) {
                account.transferAtoB(10);
            }
        });
        Thread t2 = new Thread(() -> {
            for (int i = 0; i < 1000; i++) {
                account.transferBtoA(10);
            }
        });

        t1.start();
        t2.start();
        t1.join();
        t2.join();

        System.out.println("Done (if this prints, you got lucky and avoided the deadlock)");
    }
}
