package org.example; // A declaração do pacote deve ser a PRIMEIRA linha

import javax.persistence.EntityManager;
import javax.persistence.EntityManagerFactory;
import javax.persistence.Persistence;

import org.example.Cliente;
import org.example.Produto;
import org.example.Tempo;
import org.example.Loja;
import org.example.Venda;


public class Main {

    public static void main(String[] args) {

        // Nome da unidade de persistência definida no persistence.xml
        String persistenceUnitName = "varejoPU";

        EntityManagerFactory emf = null;
        EntityManager em = null;

        try {
            // 1. Criar o EntityManagerFactory
            // Este é um recurso caro e deve ser criado apenas uma vez na aplicação
            emf = Persistence.createEntityManagerFactory(persistenceUnitName);
            System.out.println("EntityManagerFactory criado com sucesso!");

            // 2. Criar o EntityManager
            // O EntityManager é a interface principal para interagir com o contexto de persistência
            em = emf.createEntityManager();
            System.out.println("EntityManager criado com sucesso!");

            // 3. Iniciar uma transação
            // Todas as operações que modificam o banco de dados devem estar dentro de uma transação
            em.getTransaction().begin();
            System.out.println("Transação iniciada.");

            // 4. Criar instâncias das entidades
            Cliente c = new Cliente();
            c.setNome("Hian");
            c.setCidade("Recife");

            Produto p = new Produto();
            p.setNome("Notebook");
            p.setCategoria("Eletrônicos");
            // Nota: Você está usando String para data em Tempo.data.
            // Considere usar java.util.Date ou java.time.LocalDate para melhor manipulação de datas.
            Tempo t = new Tempo();
            t.setData("2024-05-19");
            t.setMes(5);
            t.setAno(2024);

            Loja l = new Loja();
            l.setNome("Loja Recife");
            l.setCidade("Recife");

            Venda v = new Venda();
            v.setCliente(c);
            v.setProduto(p);
            v.setTempo(t);
            v.setLoja(l);
            v.setQuantidade(1);
            v.setValorTotal(3500.0);

            // 5. Persistir as entidades
            // A JPA irá gerenciar as relações automaticamente devido às anotações @ManyToOne
            em.persist(c);
            em.persist(p);
            em.persist(t);
            em.persist(l);
            em.persist(v); // Persistindo a venda e as entidades relacionadas (se ainda não gerenciadas)

            System.out.println("Entidades preparadas para persistência.");

            // 6. Commit da transação
            // As mudanças são efetivamente salvas no banco de dados
            em.getTransaction().commit();
            System.out.println("Entidades persistidas com sucesso!");

        } catch (Exception e) {
            // Em caso de erro, faz rollback da transação
            if (em != null && em.getTransaction().isActive()) {
                em.getTransaction().rollback();
                System.out.println("Transação fez rollback devido a um erro.");
            }
            System.err.println("Ocorreu um erro durante a operação JPA:");
            e.printStackTrace();
        } finally {
            // 7. Fechar os recursos no bloco finally para garantir que sejam fechados
            // mesmo que ocorram exceções.
            if (em != null) {
                em.close();
                System.out.println("EntityManager fechado.");
            }
            if (emf != null) {
                emf.close();
                System.out.println("EntityManagerFactory fechado.");
            }
        }
    }
}
