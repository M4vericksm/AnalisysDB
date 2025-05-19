package org.example;

import javax.persistence.*;

@Entity
public class Venda {
    @Id
    @GeneratedValue
    private Long id;

    @ManyToOne
    private Cliente cliente;

    @ManyToOne
    private Produto produto;

    @ManyToOne
    private Tempo tempo;

    @ManyToOne
    private Loja loja;

    private int quantidade;
    private double valorTotal;

    // Getters e Setters
    public Long getId() { return id; }
    public Cliente getCliente() { return cliente; }
    public void setCliente(Cliente cliente) { this.cliente = cliente; }
    public Produto getProduto() { return produto; }
    public void setProduto(Produto produto) { this.produto = produto; }
    public Tempo getTempo() { return tempo; }
    public void setTempo(Tempo tempo) { this.tempo = tempo; }
    public Loja getLoja() { return loja; }
    public void setLoja(Loja loja) { this.loja = loja; }
    public int getQuantidade() { return quantidade; }
    public void setQuantidade(int quantidade) { this.quantidade = quantidade; }
    public double getValorTotal() { return valorTotal; }
    public void setValorTotal(double valorTotal) { this.valorTotal = valorTotal; }
}