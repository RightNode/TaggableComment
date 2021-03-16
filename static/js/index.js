$(function () {
    let base_url = "http://127.0.0.1:5000";

    /** 该函数用于响应排序和过滤请求 */
    var two_select_changed = function () {
        // 获取排序select的值
        let sorted_by = $(".commets-sort-select option:selected").attr("value");
        if (sorted_by === null)
            sorted_by = "time-down";
        let form_html = '<input type="hidden" name="sorted_by" value="' + sorted_by + '">'

        // 获取过滤bootstrap-select的选中值
        let filter_opts = $('.selectpicker').find("option:selected");
        for (var i = 0; i < filter_opts.length; i++)
            form_html += '<input type="hidden" name="filter_tag_ids[]" value="' + String(filter_opts[i].value) + '">'

        $(".ctl-form").html(form_html).submit();
    };

    /** for bootstrap-select **/
    $(".selectpicker").selectpicker({
        width: 350
    });
    // 初始化bootstrap-select以及绑定响应事件
    $('.selectpicker').selectpicker().on('hide.bs.select', two_select_changed);
    /** end for bootstrap-select **/

    /** 为排序select绑定响应事件 */
    $(".commets-sort-select").change(two_select_changed);

    /** 去掉所有a标签的下划线 */
    $("a").css("text-decoration", "none");

    /** 为各个评论的回复按钮绑定单击事件 */
    $(".cmt-reply").click(function () {
        if ($(this).text() === "回复") {
            $(this).text("取消回复");
        } else {
            $(this).text("回复");
        }
    })

    /** 为点赞按钮绑定单击事件 */
    $(".fa-thumbs-up").click(function () {
        let cmt_id = $(this).data("cmt-id");

        let this_thumb_up = $(this);
        let up_label = $(this).next();
        let next_thumb_down = up_label.next();
        let down_label = next_thumb_down.next();

        $.ajax({
            url: base_url + "/thumb_up_action",
            data: {"cmt_id": cmt_id},
            type: "POST",
            success: function () {
                if (this_thumb_up.attr("class") === "far fa-thumbs-up") {
                    this_thumb_up.attr("class", "fas fa-thumbs-up");
                    up_label.html(parseInt(up_label.html()) + 1);
                    if (next_thumb_down.attr("class") === "fas fa-thumbs-down") {
                        next_thumb_down.attr("class", "far fa-thumbs-down");
                        down_label.html(parseInt(down_label.html()) - 1);
                    }
                } else {
                    this_thumb_up.attr("class", "far fa-thumbs-up");
                    up_label.html(parseInt(up_label.html()) - 1);
                }
            }
        });
    });

    /** 为点踩按钮绑定单击事件 */
    $(".fa-thumbs-down").click(function () {
        let cmt_id = $(this).data("cmt-id");

        let this_thumb_down = $(this);
        let down_label = $(this).next();
        let up_label = $(this).prev();
        let pre_thumb_up = up_label.prev();

        $.ajax({
            url: base_url + "/thumb_down_action",
            data: {"cmt_id": cmt_id},
            type: "POST",
            success: function () {
                if (this_thumb_down.attr("class") === "far fa-thumbs-down") {
                    this_thumb_down.attr("class", "fas fa-thumbs-down");
                    down_label.html(parseInt(down_label.html()) + 1);
                    if (pre_thumb_up.attr("class") === "fas fa-thumbs-up") {
                        pre_thumb_up.attr("class", "far fa-thumbs-up");
                        up_label.html(parseInt(up_label.html()) - 1);
                    }
                } else {
                    this_thumb_down.attr("class", "far fa-thumbs-down");
                    up_label.html(parseInt(up_label.html()) - 1);
                }
            }
        });
    });

    /** 绑定点击标签时触发的事件 */
    $(".tag-span").click(function () {
        let mark_color = "#A569BD";
        let this_tag = $(this);
        let cmt_tag_id = $(this).data("cmt-tag-id");
        let marked = $(this).data("marked");
        let inner_label = $(this).find("label").eq(0);
        let pre_num = parseInt(inner_label.html());
        console.log("marked", marked, "pre_num", pre_num);

        $.ajax({
            url: base_url + "/tag_agree",
            data: {"cmt_tag_id": cmt_tag_id},
            type: "POST",
            success: function () {
                if (!marked) {
                    inner_label.html(pre_num + 1);
                    this_tag.css("color", mark_color);
                    this_tag.data("marked", true);
                } else {
                    if (pre_num !== 1) {
                        inner_label.html(pre_num - 1);
                        this_tag.css("color", "#fff");
                        this_tag.data("marked", false);
                    } else {
                        this_tag.remove();
                    }
                }
            }
        });
    });
})
